from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import pandas as pd

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

# COMPLETE STAFF CONFIGURATION with daily schedules - 29 staff members
STAFF_SCHEDULES = {
    # MANHATTAN STAFF (19 people)
    '+19175778296': {  # Delisha
        'name': 'Delisha',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Manhattan',
            'Monday': 'Manhattan',
            'Tuesday': 'Off',
            'Wednesday': 'Manhattan',
            'Thursday': 'Manhattan',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+16315208051': {  # Tina
        'name': 'Tina',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Manhattan',
            'Monday': 'Manhattan',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Off',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+19173199423': {  # Sanae
        'name': 'Sanae',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Manhattan',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Off',
            'Thursday': 'Off',
            'Friday': 'Manhattan',
            'Saturday': 'Manhattan'
        }
    },
    '+17187578709': {  # Tara
        'name': 'Tara',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Manhattan',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+19178932590': {  # Zelina
        'name': 'Zelina',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Manhattan',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Off',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+16145816298': {  # Regi
        'name': 'Regi',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Manhattan',
            'Monday': 'Manhattan',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Manhattan',
            'Thursday': 'Manhattan',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+17163162623': {  # Rabi
        'name': 'Rabi',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Manhattan',
            'Monday': 'Manhattan',
            'Tuesday': 'Queens',
            'Wednesday': 'Manhattan',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+19293287308': {  # Janaye
        'name': 'Janaye',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Off',
            'Thursday': 'Off',
            'Friday': 'Manhattan',
            'Saturday': 'Queens'
        }
    },
    '+19293739694': {  # Adrea
        'name': 'Adrea',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Manhattan',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Manhattan'
        }
    },
    '+19293725622': {  # Dalmania
        'name': 'Dalmania',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Manhattan',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Manhattan'
        }
    },
    '+15512455660': {  # Rolanda
        'name': 'Rolanda',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Manhattan',
            'Monday': 'Off',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Off',
            'Thursday': 'Manhattan',
            'Friday': 'Manhattan',
            'Saturday': 'Off'
        }
    },
    '+19174363971': {  # Jackalin
        'name': 'Jackalin',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Manhattan',
            'Wednesday': 'Off',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Brooklyn'
        }
    },
    '+19542009650': {  # Mia
        'name': 'Mia',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Queens',
            'Wednesday': 'Off',
            'Thursday': 'Manhattan',
            'Friday': 'Off',
            'Saturday': 'Manhattan'
        }
    },
    '+19172837518': {  # Jessica
        'name': 'Jessica',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Off',
            'Wednesday': 'Manhattan',
            'Thursday': 'Manhattan',
            'Friday': 'Manhattan',
            'Saturday': 'Manhattan'
        }
    },
    '+13479510800': {  # Tshazia
        'name': 'Tshazia',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Off',
            'Wednesday': 'Manhattan',
            'Thursday': 'Manhattan',
            'Friday': 'Manhattan',
            'Saturday': 'Manhattan'
        }
    },
    '+16467615002': {  # Jona-Ann
        'name': 'Jona-Ann',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Off',
            'Wednesday': 'Manhattan',
            'Thursday': 'Manhattan',
            'Friday': 'Manhattan',
            'Saturday': 'Manhattan'
        }
    },
    '+19292182196': {  # Lee (Olga Lee)
        'name': 'Lee',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Manhattan',
            'Monday': 'Off',
            'Tuesday': 'Off',
            'Wednesday': 'Off',
            'Thursday': 'Manhattan',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+13472939475': {  # Andrea
        'name': 'Andrea',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Brooklyn',
            'Tuesday': 'Off',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Off',
            'Friday': 'Manhattan',
            'Saturday': 'Manhattan'
        }
    },
    '+17189137388': {  # Briyanna
        'name': 'Briyanna',
        'home_location': 'Manhattan',
        'schedule': {
            'Sunday': 'Manhattan',
            'Monday': 'Off',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Brooklyn'
        }
    },

    # BROOKLYN STAFF (17 people)
    '+19172928301': {  # Christina
        'name': 'Christina',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Brooklyn',
            'Tuesday': 'Off',
            'Wednesday': 'Off',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Off'
        }
    },
    '+16464138781': {  # Olivia
        'name': 'Olivia',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Brooklyn',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Off',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+17704680674': {  # Carli
        'name': 'Carli',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Off',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+18624066889': {  # Ruth Calina
        'name': 'Ruth Calina',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Off',
            'Tuesday': 'Off',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Off'
        }
    },
    '+13473149438': {  # Raquel
        'name': 'Raquel',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Brooklyn',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Off',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Off'
        }
    },
    '+13472435314': {  # Lorna
        'name': 'Lorna',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Brooklyn',
            'Monday': 'Brooklyn',
            'Tuesday': 'Off',
            'Wednesday': 'Off',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Off'
        }
    },
    '+19177146698': {  # Khadijah
        'name': 'Khadijah',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Brooklyn',
            'Tuesday': 'Off',
            'Wednesday': 'Off',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Brooklyn'
        }
    },
    '+13477944000': {  # Kimberly
        'name': 'Kimberly',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Brooklyn',
            'Tuesday': 'Off',
            'Wednesday': 'Off',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Brooklyn'
        }
    },
    '+19174127601': {  # Colleen
        'name': 'Colleen',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Brooklyn',
            'Tuesday': 'Queens',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Queens',
            'Friday': 'Queens',
            'Saturday': 'Queens'
        }
    },
    '+18457458091': {  # Jessica.A
        'name': 'Jessica.A',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Off',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Brooklyn'
        }
    },
    '+13477727743': {  # Sharon
        'name': 'Sharon',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Brooklyn',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Off',
            'Friday': 'Off',
            'Saturday': 'Brooklyn'
        }
    },
    '+19296276655': {  # Maiyah
        'name': 'Maiyah',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Off',
            'Wednesday': 'Brooklyn',
            'Thursday': 'Brooklyn',
            'Friday': 'Brooklyn',
            'Saturday': 'Brooklyn'
        }
    },

    # QUEENS STAFF (6 people)
    '+16465893995': {  # Maura
        'name': 'Maura',
        'home_location': 'Queens',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Queens',
            'Wednesday': 'Off',
            'Thursday': 'Queens',
            'Friday': 'Queens',
            'Saturday': 'Queens'
        }
    },
    '+16463745159': {  # Lerdy
        'name': 'Lerdy',
        'home_location': 'Queens',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Off',
            'Tuesday': 'Off',
            'Wednesday': 'Off',
            'Thursday': 'Queens',
            'Friday': 'Queens',
            'Saturday': 'Queens'
        }
    },

    # EXISTING STAFF (keep your entry)
    '+16316243242': {  # Evan
        'name': 'Evan',
        'home_location': 'Brooklyn',
        'schedule': {
            'Sunday': 'Off',
            'Monday': 'Brooklyn',
            'Tuesday': 'Manhattan', 
            'Wednesday': 'Brooklyn',
            'Thursday': 'Brooklyn',
            'Friday': 'Manhattan',
            'Saturday': 'Brooklyn'
        }
    }
}

# In-memory storage for pending call-outs (staff waiting to specify location)
# In production, you'd want to use a database, but this works for now
PENDING_CALLOUTS = {}

def get_scheduled_location_for_today(phone_number):
    """
    Get where staff is scheduled to work today according to their schedule
    Used for display purposes only - shows staff what their schedule says
    """
    if phone_number not in STAFF_SCHEDULES:
        return None
    
    staff_info = STAFF_SCHEDULES[phone_number]
    day_name = datetime.now().strftime('%A')
    
    scheduled_location = staff_info['schedule'].get(day_name, 'Off')
    
    # If they're scheduled to be off, return their home location as fallback
    if scheduled_location == 'Off':
        return staff_info['home_location']
    
    return scheduled_location

def parse_location_choice(message_body):
    """
    Parse the location choice from staff response (1, 2, or 3)
    Returns the location name or None if invalid
    """
    message_clean = message_body.strip().lower()
    
    # Handle various formats: "1", " 1 ", "1.", "option 1", etc.
    if '1' in message_clean:
        return 'Manhattan'
    elif '2' in message_clean:
        return 'Brooklyn'
    elif '3' in message_clean:
        return 'Queens'
    else:
        return None

def get_staff_schedule_display():
    """
    Generate HTML table showing all staff schedules
    """
    df_staff = pd.DataFrame([
        {
            'Name': info['name'],
            'Phone': phone,
            'Home Location': info['home_location'],
            **info['schedule']
        }
        for phone, info in STAFF_SCHEDULES.items()
    ])
    
    return df_staff.to_html(index=False, classes='staff-schedule-table')

def get_manager_phones():
    """Get all manager phone numbers from the routing system"""
    manager_contacts = routing_system.get_manager_contact_info(
        routing_system.df_schedule['Manager Name'].tolist()
    )
    return [contact['phone'] for contact in manager_contacts]

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
            <li>System responds asking which location they were scheduled for today</li>
            <li>Staff reply with: 1 for Manhattan, 2 for Brooklyn, 3 for Queens</li>
            <li>System uses sophisticated routing logic to find best available manager</li>
            <li>Staff receives confirmation of who was notified</li>
        </ol>
        
        <h2>Test Links:</h2>
        <ul>
            <li><a href="/test-routing">Test Routing Logic</a></li>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/schedule">View Manager Schedule</a></li>
            <li><a href="/staff-schedule">View Staff Schedule</a></li>
            <li><a href="/pending-callouts">View Pending Call-Outs</a></li>
        </ul>
        
        <p><em>Last updated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</em></p>
    </body>
    </html>
    '''

@app.route('/webhook/sms', methods=['POST'])
def handle_incoming_sms():
    """Handle incoming SMS with two-step location confirmation process"""
    
    # Get message details from Twilio
    from_phone = request.form.get('From')
    message_body = request.form.get('Body', '')
    
    logger.info(f"Received SMS from {from_phone}: {message_body}")
    
    # Create response object
    resp = MessagingResponse()
    
    try:
        # Check if this is a manager responding to a call-out
        manager_phones = routing_system.get_manager_contact_info(
            routing_system.df_schedule['Manager Name'].tolist()
        )
        manager_phone_list = [contact['phone'] for contact in manager_phones]
        
        if from_phone in manager_phone_list:
            resp.message("✅ Thank you for confirming receipt of the call-out alert.")
            logger.info(f"Manager {from_phone} confirmed receipt: {message_body}")
            return str(resp)

        # Verify this is from a known staff member
        if from_phone not in STAFF_SCHEDULES:
            error_msg = f"❌ Unknown phone number {from_phone}. Please contact IT support to register your number."
            logger.warning(error_msg)
            resp.message(error_msg)
            return str(resp)
        
        staff_info = STAFF_SCHEDULES[from_phone]
        staff_name = staff_info['name']
        staff_home_location = staff_info['home_location']
        
        # Get current time for routing decision
        current_time = datetime.now()
        
        # Check if this is a location response (second message in the flow)
        if from_phone in PENDING_CALLOUTS:
            # This is the staff responding with their location choice
            chosen_location = parse_location_choice(message_body)
            
            if not chosen_location:
                # Invalid choice - ask again
                resp.message("""❌ Please reply with a valid option:

1 - Manhattan
2 - Brooklyn  
3 - Queens

Which location were you scheduled to work at today?""")
                logger.warning(f"Invalid location choice from {from_phone}: {message_body}")
                return str(resp)
            
            # Valid location choice - proceed with routing
            original_message = PENDING_CALLOUTS[from_phone]['original_message']
            original_time = PENDING_CALLOUTS[from_phone]['timestamp']
            
            # Remove from pending (call-out is now being processed)
            del PENDING_CALLOUTS[from_phone]
            
            logger.info(f"Processing call-out: {staff_name} (Home: {staff_home_location}, Working: {chosen_location})")
            
            # Determine responsible managers using sophisticated routing logic:
            # 1. Check 8 PM rule (look to next day if after 8 PM)
            # 2. Check if DIRECT manager (at working location) is actively working
            # 3. Check if AWAY managers are actively working  
            # 4. Compare start times: away manager vs direct manager
            # 5. Fallback to HOME manager if staff working away from home
            # 6. Emergency fallbacks
            responsible_managers = routing_system.determine_responsible_manager(
                staff_home_location, 
                chosen_location, 
                original_time
            )
            
            if not responsible_managers:
                error_msg = "❌ No managers available. Please call the emergency line immediately."
                logger.error("No responsible managers found")
                resp.message(error_msg)
                return str(resp)
            
            # Get manager contact info
            manager_contacts = routing_system.get_manager_contact_info(responsible_managers)
            
            # Create formatted message for managers
            day_name = original_time.strftime('%A')
            manager_message = f"""🚨 STAFF CALL-OUT ALERT

Staff: {staff_name}
Phone: {from_phone}
Home Location: {staff_home_location}
Working Today ({day_name}): {chosen_location}
Time: {original_time.strftime('%A, %B %d at %I:%M %p')}

Original Message: "{original_message}"

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
                confirmation = f"""✅ Call-out processed and forwarded to:

{chr(10).join(['• ' + manager for manager in sent_to])}

Location confirmed: {chosen_location}

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
            
        else:
            # This is the initial call-out message - ask for location confirmation
            scheduled_location = get_scheduled_location_for_today(from_phone)
            
            # Store the call-out details for when they respond with location
            PENDING_CALLOUTS[from_phone] = {
                'original_message': message_body,
                'timestamp': current_time,
                'staff_name': staff_name,
                'staff_home_location': staff_home_location
            }
            
            # Ask them to confirm their working location
            location_request = f"""📋 Call-out received, {staff_name}.

Which location were you scheduled to work at today?

1 - Manhattan
2 - Brooklyn
3 - Queens

(Your schedule shows: {scheduled_location})

Please reply with 1, 2, or 3."""
            
            resp.message(location_request)
            logger.info(f"Initial call-out from {staff_name}, requesting location confirmation")
        
    except Exception as e:
        error_msg = f"❌ System error processing your call-out. Please call the emergency line. Error: {str(e)}"
        logger.error(f"Error processing call-out from {from_phone}: {e}")
        resp.message("❌ System error. Please call the emergency line immediately.")
        
        # Clean up any pending call-out for this number
        if from_phone in PENDING_CALLOUTS:
            del PENDING_CALLOUTS[from_phone]
    
    return str(resp)

@app.route('/pending-callouts')
def view_pending_callouts():
    """View staff members who are waiting to confirm their location"""
    try:
        if not PENDING_CALLOUTS:
            return '''
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; padding: 20px;">
                <h2>📋 Pending Call-Outs</h2>
                <p>✅ No pending call-outs at this time.</p>
                <p><a href="/">← Back to Home</a></p>
            </body>
            </html>
            '''
        
        pending_html = "<ul>"
        for phone, details in PENDING_CALLOUTS.items():
            time_str = details['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            pending_html += f"""
            <li>
                <strong>{details['staff_name']}</strong> ({phone})<br>
                Time: {time_str}<br>
                Message: "{details['original_message']}"<br>
                <em>Waiting for location confirmation...</em>
            </li><br>
            """
        pending_html += "</ul>"
        
        return f'''
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px;">
            <h2>📋 Pending Call-Outs</h2>
            <p><strong>Staff waiting to confirm their location:</strong></p>
            {pending_html}
            <p><a href="/">← Back to Home</a></p>
        </body>
        </html>
        '''
    except Exception as e:
        return f'<html><body><h2>❌ Error:</h2><p>{str(e)}</p><p><a href="/">← Back to Home</a></p></body></html>'

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
            
            # Parse the test time string to create a datetime object
            try:
                # Handle formats like "Tuesday 10:30" or "Tuesday 10:30 AM"
                if any(day in test_time_str for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
                    parts = test_time_str.split()
                    if len(parts) >= 2:
                        day_name = parts[0]
                        time_str = parts[1]
                        
                        # Convert to datetime object
                        from datetime import timedelta
                        today = datetime.now()
                        days_ahead = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(day_name) - today.weekday()
                        if days_ahead <= 0:
                            days_ahead += 7
                        target_date = today + timedelta(days=days_ahead)
                        
                        # Parse time (handle both 24hr and 12hr formats)
                        try:
                            if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                                test_time = datetime.strptime(time_str, '%I:%M %p').time()
                            else:
                                test_time = datetime.strptime(time_str, '%H:%M').time()
                        except:
                            test_time = datetime.strptime(time_str, '%H:%M').time()
                        
                        test_datetime = datetime.combine(target_date.date(), test_time)
                    else:
                        test_datetime = datetime.now()
                else:
                    test_datetime = datetime.strptime(test_time_str, '%Y-%m-%d %H:%M')
            except:
                test_datetime = datetime.now()
            
            # DEBUG: Add logging to see what's happening
            logger.info(f"DEBUG: Testing with staff_home={staff_home}, staff_working={staff_working}, datetime={test_datetime}")
            
            # Check what managers are found by location
            direct_managers = routing_system.get_managers_by_location(staff_working)
            logger.info(f"DEBUG: Direct managers for {staff_working}: {direct_managers}")
            
            # Check if manager is working
            if direct_managers:
                for manager in direct_managers:
                    is_working = routing_system.is_manager_working(manager, test_datetime)
                    logger.info(f"DEBUG: Is {manager} working at {test_datetime}? {is_working}")
            
            # Use the routing system directly like the SMS handler does
            responsible_managers = routing_system.determine_responsible_manager(
                staff_home, 
                staff_working, 
                test_datetime
            )
            
            logger.info(f"DEBUG: Responsible managers returned: {responsible_managers}")
            
            # Get contact info for the responsible managers
            contact_info = routing_system.get_manager_contact_info(responsible_managers)
            logger.info(f"DEBUG: Contact info returned: {contact_info}")
            
            result = {
                'success': True,
                'responsible_managers': responsible_managers,
                'contact_info': contact_info,
                'test_time': test_time_str,
                'staff_home_location': staff_home,
                'staff_working_location': staff_working,
                'parsed_datetime': test_datetime.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if request.is_json:
                return jsonify(result)
            else:
                # Return HTML response for form submission
                if contact_info:
                    managers_list = '<br>'.join([f"• {c['name']} at {c['location']} ({c['phone']})" for c in contact_info])
                else:
                    managers_list = "❌ No managers found (check routing logic)"
                
                direct_managers_display = ', '.join(direct_managers) if 'direct_managers' in locals() else 'Unknown'
                responsible_managers_display = ', '.join(responsible_managers) if responsible_managers else 'None'
                
                return f'''
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; padding: 20px;">
                    <h2>✅ Routing Test Results</h2>
                    <p><strong>Staff Home Location:</strong> {staff_home}</p>
                    <p><strong>Staff Working Location:</strong> {staff_working}</p>
                    <p><strong>Test Time:</strong> {test_time_str}</p>
                    <p><strong>Parsed DateTime:</strong> {test_datetime.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <h3>Responsible Managers:</h3>
                    <p>{managers_list}</p>
                    <h3>Debug Info:</h3>
                    <p><strong>Manager Names:</strong> {responsible_managers_display}</p>
                    <p><strong>Total Contacts:</strong> {len(contact_info)}</p>
                    <p><strong>Direct Managers Found:</strong> {direct_managers_display}</p>
                    <p><em>Check server logs for detailed debug information</em></p>
                    <p><a href="/test-routing">← Test Again</a></p>
                </body>
                </html>
                '''
                
        except Exception as e:
            error_result = {'success': False, 'error': str(e)}
            logger.error(f"DEBUG: Exception in test routing: {e}")
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

@app.route('/staff-schedule')
def view_staff_schedule():
    """View current staff schedule"""
    try:
        schedule_html = get_staff_schedule_display()
        
        return f'''
        <html>
        <head>
            <title>Staff Schedule</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 20px auto; padding: 20px; }}
                .staff-schedule-table {{ border-collapse: collapse; width: 100%; }}
                .staff-schedule-table th, .staff-schedule-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .staff-schedule-table th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h2>👥 Staff Weekly Schedule</h2>
            
            <div class="summary">
                <h3>📊 Summary</h3>
                <p><strong>Total Staff:</strong> {len(STAFF_SCHEDULES)}</p>
                <p><strong>Locations Covered:</strong> Brooklyn, Manhattan, Queens</p>
                <p><strong>Two-Step Process:</strong> Staff confirm location via SMS</p>
                <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            {schedule_html}
            
            <h3>📝 How It Works:</h3>
            <ul>
                <li><strong>Step 1:</strong> Staff text call-out message</li>
                <li><strong>Step 2:</strong> System asks for location confirmation (1/2/3)</li>
                <li><strong>Schedule Display:</strong> Shows staff what their schedule says (for reference)</li>
                <li><strong>Sophisticated Routing:</strong> Uses complex logic to find best available manager</li>
                <li><strong>No Parsing:</strong> 100% reliable location confirmation</li>
            </ul>
            
            <p><a href="/">← Back to Home</a> | <a href="/schedule">View Manager Schedule</a> | <a href="/pending-callouts">View Pending Call-Outs</a></p>
        </body>
        </html>
        '''
    except Exception as e:
        return f'<html><body><h2>❌ Error loading staff schedule:</h2><p>{str(e)}</p><p><a href="/">← Back to Home</a></p></body></html>'

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
            'schedule_loaded': routing_system.df_schedule is not None,
            'total_staff': len(STAFF_SCHEDULES),
            'pending_callouts': len(PENDING_CALLOUTS),
            'two_step_sms': True
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