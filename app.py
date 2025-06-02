from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your routing system
from routing_system import CallOutRoutingSystem

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Initialize routing system
routing_system = CallOutRoutingSystem()

# Staff phone number to location mapping
# TODO: Update these with real phone numbers
STAFF_LOCATIONS = {
    '+6316243242': {'home': 'Brooklyn', 'name': 'Evan'},
    '+15552222222': {'home': 'Manhattan', 'name': 'Jane Smith'},
    '+15553333333': {'home': 'Brooklyn', 'name': 'Mike Johnson'},
    '+15554444444': {'home': 'Manhattan', 'name': 'Sarah Wilson'},
}

def parse_working_location(message_content, staff_home_location):
    """
    Parse the working location from the message content
    Staff can specify where they're working, otherwise defaults to home location
    """
    message_lower = message_content.lower()
    
    # Look for location keywords
    if any(word in message_lower for word in ['manhattan', 'mnh', 'man']):
        return 'Manhattan'
    elif any(word in message_lower for word in ['brooklyn', 'bkn', 'brk']):
        return 'Brooklyn'
    elif any(word in message_lower for word in ['queens', 'qns', 'que']):
        return 'Queens'
    else:
        # Default to home location if not specified
        return staff_home_location

def send_sms(to_phone, message):
    """Send SMS via Twilio"""
    try:
        message_obj = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        logger.info(f"SMS sent to {to_phone}: {message_obj.sid}")
        return True, message_obj.sid
    except Exception as e:
        logger.error(f"Failed to send SMS to {to_phone}: {e}")
        return False, str(e)

@app.route('/')
def home():
    """Home page with basic info"""
    return '''
    <html>
    <head><title>Call-Out Routing System</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
        <h1>🚨 Call-Out Routing System</h1>
        <p><strong>Status:</strong> Active and monitoring</p>
        <p><strong>Twilio Number:</strong> ''' + str(TWILIO_PHONE_NUMBER) + '''</p>
        
        <h2>How to Use:</h2>
        <ol>
            <li>Staff text the Twilio number with their call-out message</li>
            <li>Include location if working away from home: "Can't come in today - working at Manhattan"</li>
            <li>System automatically routes to appropriate manager</li>
            <li>Staff receives confirmation of who was notified</li>
        </ol>
        
        <h2>Test Links:</h2>
        <ul>
            <li><a href="/test-routing">Test Routing Logic</a></li>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/schedule">View Current Schedule</a></li>
        </ul>
        
        <p><em>Last updated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</em></p>
    </body>
    </html>
    '''

@app.route('/webhook/sms', methods=['POST'])
def handle_incoming_sms():
    """Handle incoming SMS from staff call-outs"""
    
    # Get message details from Twilio
    from_phone = request.form.get('From')
    message_body = request.form.get('Body', '')
    
    logger.info(f"Received SMS from {from_phone}: {message_body}")
    
    # Create response object
    resp = MessagingResponse()
    
    try:
        # Verify this is from a known staff member
        if from_phone not in STAFF_LOCATIONS:
            error_msg = f"❌ Unknown phone number {from_phone}. Please contact IT support to register your number."
            logger.warning(error_msg)
            resp.message(error_msg)
            return str(resp)
        
        staff_info = STAFF_LOCATIONS[from_phone]
        staff_name = staff_info['name']
        staff_home_location = staff_info['home']
        
        # Parse working location from message
        staff_working_location = parse_working_location(message_body, staff_home_location)
        
        # Get current time for routing decision
        current_time = datetime.now()
        
        logger.info(f"Processing call-out: {staff_name} (Home: {staff_home_location}, Working: {staff_working_location})")
        
        # Determine responsible managers using your routing logic
        responsible_managers = routing_system.determine_responsible_manager(
            staff_home_location, 
            staff_working_location, 
            current_time
        )
        
        if not responsible_managers:
            error_msg = "❌ No managers available. Please call the emergency line immediately."
            logger.error("No responsible managers found")
            resp.message(error_msg)
            return str(resp)
        
        # Get manager contact info
        manager_contacts = routing_system.get_manager_contact_info(responsible_managers)
        
        # Create formatted message for managers
        manager_message = f"""🚨 STAFF CALL-OUT ALERT

Staff: {staff_name}
Phone: {from_phone}
Home Location: {staff_home_location}
Working Today: {staff_working_location}
Time: {current_time.strftime('%A, %B %d at %I:%M %p')}

Message: "{message_body}"

Please respond to confirm receipt."""
        
        # Send notifications to responsible managers
        sent_to = []
        failed_to = []
        
        for manager in manager_contacts:
            success, result = send_sms(manager['phone'], manager_message)
            if success:
                sent_to.append(f"{manager['name']} at {manager['location']}")
                logger.info(f"Notified manager: {manager['name']} ({manager['phone']})")
            else:
                failed_to.append(f"{manager['name']}: {result}")
                logger.error(f"Failed to notify {manager['name']}: {result}")
        
        # Send confirmation back to staff
        if sent_to:
            confirmation = f"""✅ Call-out received and forwarded to:

{chr(10).join(['• ' + manager for manager in sent_to])}

Your manager(s) will respond shortly."""
            
            if failed_to:
                confirmation += f"""

⚠️ Could not reach:
{chr(10).join(['• ' + manager for manager in failed_to])}"""
                
        else:
            confirmation = "❌ Failed to reach any managers. Please call the emergency line immediately."
        
        resp.message(confirmation)
        
        # Log successful processing
        logger.info(f"Call-out processed successfully: {staff_name} → {len(sent_to)} managers notified")
        
    except Exception as e:
        error_msg = f"❌ System error processing your call-out. Please call the emergency line. Error: {str(e)}"
        logger.error(f"Error processing call-out from {from_phone}: {e}")
        resp.message("❌ System error. Please call the emergency line immediately.")
    
    return str(resp)

@app.route('/test-routing', methods=['GET', 'POST'])
def test_routing_endpoint():
    """Test endpoint to verify routing logic"""
    if request.method == 'POST':
        try:
            # Handle both form and JSON data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            staff_home = data.get('staff_home_location')
            staff_working = data.get('staff_working_location') 
            test_time_str = data.get('test_time', datetime.now().strftime('%A %H:%M'))
            
            responsible_managers, contact_info = routing_system.test_routing(
                staff_home, staff_working, test_time_str
            )
            
            result = {
                'success': True,
                'responsible_managers': responsible_managers,
                'contact_info': contact_info,
                'test_time': test_time_str,
                'staff_home_location': staff_home,
                'staff_working_location': staff_working
            }
            
            if request.is_json:
                return jsonify(result)
            else:
                # Return HTML response for form submission
                managers_list = '<br>'.join([f"• {c['name']} at {c['location']} ({c['phone']})" for c in contact_info])
                return f'''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; padding: 20px;">
                    <h2>✅ Routing Test Results</h2>
                    <p><strong>Staff Home Location:</strong> {staff_home}</p>
                    <p><strong>Staff Working Location:</strong> {staff_working}</p>
                    <p><strong>Test Time:</strong> {test_time_str}</p>
                    <h3>Responsible Managers:</h3>
                    <p>{managers_list}</p>
                    <p><a href="/test-routing">← Test Again</a></p>
                </body>
                </html>
                '''
                
        except Exception as e:
            error_result = {'success': False, 'error': str(e)}
            if request.is_json:
                return jsonify(error_result), 400
            else:
                return f'<html><body><h2>❌ Error:</h2><p>{str(e)}</p><p><a href="/test-routing">← Try Again</a></p></body></html>'
    
    # GET request - return test form
    return '''
    <html>
    <head><title>Test Call-Out Routing</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px;">
        <h2>🧪 Test Call-Out Routing</h2>
        <form method="post">
            <p>
                <label><strong>Staff Home Location:</strong></label><br>
                <select name="staff_home_location" required style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="">Select...</option>
                    <option value="Brooklyn">Brooklyn</option>
                    <option value="Manhattan">Manhattan</option>
                    <option value="Queens">Queens</option>
                </select>
            </p>
            <p>
                <label><strong>Staff Working Location Today:</strong></label><br>
                <select name="staff_working_location" required style="width: 100%; padding: 8px; margin-top: 5px;">
                    <option value="">Select...</option>
                    <option value="Brooklyn">Brooklyn</option>
                    <option value="Manhattan">Manhattan</option>
                    <option value="Queens">Queens</option>
                </select>
            </p>
            <p>
                <label><strong>Test Time:</strong></label><br>
                <input type="text" name="test_time" placeholder="Tuesday 10:30" required 
                       style="width: 100%; padding: 8px; margin-top: 5px;">
                <small>Format: DayName HH:MM (e.g., "Wednesday 14:30")</small>
            </p>
            <p>
                <button type="submit" style="background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">
                    Test Routing
                </button>
            </p>
        </form>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    '''

@app.route('/schedule')
def view_schedule():
    """View current manager schedule"""
    try:
        schedule_html = routing_system.df_schedule.to_html(index=False, classes='schedule-table')
        
        return f'''
        <html>
        <head>
            <title>Manager Schedule</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 20px auto; padding: 20px; }}
                .schedule-table {{ border-collapse: collapse; width: 100%; }}
                .schedule-table th, .schedule-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .schedule-table th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h2>📅 Current Manager Schedule</h2>
            <p><strong>Last Updated:</strong> {routing_system.last_updated}</p>
            {schedule_html}
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        '''
    except Exception as e:
        return f'<html><body><h2>❌ Error loading schedule:</h2><p>{str(e)}</p><p><a href="/">← Back to Home</a></p></body></html>'

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test routing system
        routing_system.get_schedule()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'twilio_configured': bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN),
            'phone_number': TWILIO_PHONE_NUMBER,
            'schedule_loaded': routing_system.df_schedule is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)