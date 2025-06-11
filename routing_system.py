# Simplified version of the routing system for the webhook
import pandas as pd
from datetime import datetime, time, timedelta

class CallOutRoutingSystem:
    def __init__(self):
        # Your existing schedule data
        self.manager_schedule = {
            'Manager Name': ['Dia', 'Kat'],
            'Location': ['Brooklyn', 'Manhattan'],
            'Phone Number': ['+13473150211', '+13477168143'],
            'Sunday': ['-', '-'],
            'Monday': ['-', '8:45 AM - 4:45 PM'],
            'Tuesday': ['12:00 PM - 8:00 PM', '8:45 AM - 4:45 PM'],
            'Wednesday': ['8:45 AM - 5:30 PM', '8:45 AM - 4:45 PM'],
            'Thursday': ['8:45 AM - 5:30 PM', '12:00 PM - 8:00 PM'],
            'Friday': ['8:45 AM - 5:30 PM', '8:45 AM - 4:45 PM'],
            'Saturday': ['10:45 AM - 6:00 PM', '-']
        }
        
        self.df_schedule = pd.DataFrame(self.manager_schedule)
        self.last_updated = datetime.now()
    
    def parse_time_string(self, time_str):
        """Parse time string like '8:45 AM' to datetime.time object"""
        if time_str == '-' or pd.isna(time_str) or time_str == '':
            return None
        
        # Handle range format like '8:45 AM - 4:45 PM'
        if ' - ' in str(time_str):
            start_time, end_time = str(time_str).split(' - ')
            start = datetime.strptime(start_time.strip(), '%I:%M %p').time()
            end = datetime.strptime(end_time.strip(), '%I:%M %p').time()
            return (start, end)
        else:
            return datetime.strptime(str(time_str).strip(), '%I:%M %p').time()
    
    def get_day_name(self, date_obj):
        """Get day name from datetime object"""
        return date_obj.strftime('%A')
    
    def is_manager_working(self, manager_name, check_datetime):
        """Check if a manager is working at a specific datetime"""
        day_name = self.get_day_name(check_datetime)
        manager_row = self.df_schedule[self.df_schedule['Manager Name'] == manager_name]
        
        if manager_row.empty:
            return False
        
        schedule_entry = manager_row[day_name].iloc[0]
        parsed_schedule = self.parse_time_string(schedule_entry)
        
        if parsed_schedule is None:
            return False
        
        start_time, end_time = parsed_schedule
        check_time = check_datetime.time()
        
        # Handle overnight shifts (if end_time is before start_time)
        if end_time < start_time:
            return check_time >= start_time or check_time <= end_time
        else:
            return start_time <= check_time <= end_time
    
    def get_managers_by_location(self, location):
        """Get all managers for a specific location"""
        return self.df_schedule[self.df_schedule['Location'] == location]['Manager Name'].tolist()
    
    def get_next_manager_on_duty(self, location, check_datetime):
        """Find the next manager scheduled to work at a location"""
        managers_at_location = self.df_schedule[self.df_schedule['Location'] == location]
        
        # Check current day first
        for _, manager in managers_at_location.iterrows():
            day_name = self.get_day_name(check_datetime)
            schedule_entry = manager[day_name]
            parsed_schedule = self.parse_time_string(schedule_entry)
            
            if parsed_schedule:
                start_time, _ = parsed_schedule
                if start_time > check_datetime.time():
                    return manager['Manager Name'], start_time
        
        # Check next 7 days
        for days_ahead in range(1, 8):
            future_date = check_datetime + timedelta(days=days_ahead)
            day_name = self.get_day_name(future_date)
            
            for _, manager in managers_at_location.iterrows():
                schedule_entry = manager[day_name]
                parsed_schedule = self.parse_time_string(schedule_entry)
                
                if parsed_schedule:
                    start_time, _ = parsed_schedule
                    return manager['Manager Name'], start_time
        
        return None, None
    
    def determine_responsible_manager(self, staff_home_location, staff_working_location, callout_datetime):
        """Main logic to determine responsible manager(s) for a call-out"""
        
        # CHECK FOR TIMED MANAGER OVERRIDE (NEW CODE)
        import os
        from datetime import datetime
        
        override_manager = os.environ.get('MANAGER_OVERRIDE')
        override_start = os.environ.get('MANAGER_OVERRIDE_START')
        override_end = os.environ.get('MANAGER_OVERRIDE_END')
        
        if override_manager and override_start and override_end:
            try:
                start_datetime = datetime.strptime(override_start, '%Y-%m-%d %H:%M')
                end_datetime = datetime.strptime(override_end, '%Y-%m-%d %H:%M')
                current_datetime = callout_datetime
                
                # Check if current time is within override period
                if start_datetime <= current_datetime <= end_datetime:
                    if override_manager in self.df_schedule['Manager Name'].values:
                        return [override_manager]
            except ValueError:
                # If date format is wrong, ignore override and use normal logic
                pass
        
        # EXISTING LOGIC CONTINUES BELOW (UNCHANGED)
        # Get managers at staff's working location (DIRECT MANAGERS)
        direct_managers = self.get_managers_by_location(staff_working_location)
        
        # Get managers at staff's home location (HOME MANAGERS)
        home_managers = self.get_managers_by_location(staff_home_location)
        
        # Check if it's after 8 PM - look to next day
        if callout_datetime.time() >= time(20, 0):  # 8:00 PM
            next_day = callout_datetime + timedelta(days=1)
            next_day_start = datetime.combine(next_day.date(), time(0, 0))
            return self.determine_responsible_manager(staff_home_location, staff_working_location, next_day_start)
        
        # 1. PRIORITY: Check if any DIRECT manager (at working location) is actively working
        actively_working_direct_managers = []
        for manager in direct_managers:
            if self.is_manager_working(manager, callout_datetime):
                actively_working_direct_managers.append(manager)
        
        if actively_working_direct_managers:
            return actively_working_direct_managers
        
        # 2. Check for next scheduled DIRECT manager at working location
        next_direct_manager, next_direct_time = self.get_next_manager_on_duty(staff_working_location, callout_datetime)
        
        # 3. Check AWAY managers (all other locations)
        away_managers_info = []
        all_other_locations = self.df_schedule[self.df_schedule['Location'] != staff_working_location]
        
        for _, manager in all_other_locations.iterrows():
            manager_name = manager['Manager Name']
            
            # Check if away manager is actively working
            if self.is_manager_working(manager_name, callout_datetime):
                away_managers_info.append({
                    'name': manager_name,
                    'location': manager['Location'],
                    'status': 'actively_working',
                    'is_home_manager': manager['Location'] == staff_home_location
                })
            else:
                # Check when away manager starts next
                day_name = self.get_day_name(callout_datetime)
                schedule_entry = manager[day_name]
                parsed_schedule = self.parse_time_string(schedule_entry)
                
                if parsed_schedule:
                    start_time, _ = parsed_schedule
                    if start_time > callout_datetime.time():
                        away_managers_info.append({
                            'name': manager_name,
                            'location': manager['Location'],
                            'status': 'scheduled_later',
                            'start_time': start_time,
                            'is_home_manager': manager['Location'] == staff_home_location
                        })
        
        # Check if any away manager is actively working
        actively_working_away = [m for m in away_managers_info if m['status'] == 'actively_working']
        if actively_working_away:
            return [m['name'] for m in actively_working_away]
        
        # 4. Compare next scheduled times between direct and away managers
        if next_direct_manager and next_direct_time:
            # Check if any away manager starts earlier than direct manager
            earlier_away_managers = []
            for manager_info in away_managers_info:
                if manager_info['status'] == 'scheduled_later':
                    if manager_info['start_time'] < next_direct_time:
                        earlier_away_managers.append(manager_info['name'])
            
            if earlier_away_managers:
                return earlier_away_managers
            else:
                return [next_direct_manager]
        
        # 5. If no direct manager is scheduled, check home managers (if different from working location)
        if staff_home_location != staff_working_location:
            # Check for actively working home managers
            actively_working_home_managers = []
            for manager in home_managers:
                if self.is_manager_working(manager, callout_datetime):
                    actively_working_home_managers.append(manager)
            
            if actively_working_home_managers:
                return actively_working_home_managers
            
            # Check for next scheduled home manager
            next_home_manager, next_home_time = self.get_next_manager_on_duty(staff_home_location, callout_datetime)
            if next_home_manager:
                return [next_home_manager]
        
        # 6. Fallback - return direct managers anyway (or home managers if same location)
        if direct_managers:
            return direct_managers
        elif home_managers:
            return home_managers
        
        # 7. Final fallback - return any available manager
        all_managers = self.df_schedule['Manager Name'].tolist()
        return all_managers
    
    def get_manager_contact_info(self, manager_names):
        """Get contact information for managers"""
        contact_info = []
        for manager_name in manager_names:
            manager_row = self.df_schedule[self.df_schedule['Manager Name'] == manager_name]
            if not manager_row.empty:
                contact_info.append({
                    'name': manager_name,
                    'location': manager_row['Location'].iloc[0],
                    'phone': manager_row['Phone Number'].iloc[0]
                })
        return contact_info
    
    def get_schedule(self):
        """Get current schedule"""
        return self.df_schedule
    
    def print_schedule_table(self):
        """Print the current manager schedule table"""
        print(f"\n=== CURRENT MANAGER SCHEDULE ===")
        print(f"Last Updated: {self.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        print(self.df_schedule.to_string(index=False))
    
    def test_routing(self, staff_home_location, staff_working_location, test_input):
        """Test the routing system"""
        try:
            # Parse input
            if any(day in test_input for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
                parts = test_input.split()
                if len(parts) != 2:
                    raise ValueError("Day of week format should be 'DayName HH:MM'")
                
                day_name = parts[0]
                time_str = parts[1]
                
                today = datetime.now()
                days_ahead = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(day_name) - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                
                test_time = datetime.strptime(time_str, '%H:%M').time()
                test_datetime = datetime.combine(target_date.date(), test_time)
            else:
                test_datetime = datetime.strptime(test_input, '%Y-%m-%d %H:%M')
            
            # Determine responsible managers
            responsible_managers = self.determine_responsible_manager(staff_home_location, staff_working_location, test_datetime)
            
            # Get contact info
            contact_info = self.get_manager_contact_info(responsible_managers)
            
            return responsible_managers, contact_info
            
        except Exception as e:
            raise ValueError(f"Error in test_routing: {e}")
