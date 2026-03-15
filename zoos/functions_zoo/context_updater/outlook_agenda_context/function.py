from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from ascii_colors import ASCIIColors, trace_exception
import win32com.client
from datetime import datetime, timedelta
import json
import os
import pipmaster as pm
from typing import List
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
# Install required packages
if not pm.is_installed("pywin32"):
    pm.install("pywin32")

class OutlookAgendaContext(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        static_parameters = TypedConfig(
            ConfigTemplate([
                {
                    "name": "sync_days_ahead",
                    "type": "int",
                    "value": 7,
                    "help": "Sync days ahead."
                },
                {
                    "name": "cache_duration",
                    "type": "int",
                    "value": 15,
                    "help": "The number of times to retry the request if it fails or times out."
                },
            ]),
            BaseConfig(config={
            })
        )
        super().__init__("outlook_agenda_context", app, FunctionType.CONTEXT_UPDATE, client, static_parameters)
        self.sync_days_ahead = static_parameters.sync_days_ahead
        self.cache_duration = static_parameters.cache_duration
        self.cache_file = os.path.join(app.lollms_paths.personal_outputs_path, 'outlook_cache.json')
        self.last_sync = None

    def needs_sync(self):
        if not os.path.exists(self.cache_file):
            return True
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                last_sync = datetime.fromisoformat(cache_data['last_sync'])
                if datetime.now() - last_sync > timedelta(minutes=self.cache_duration):
                    return True
        except:
            return True
        return False

    def sync_with_outlook(self):
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            calendar = namespace.GetDefaultFolder(9)  # 9 is the calendar folder

            # Get date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=self.sync_days_ahead)

            # Get appointments
            appointments = calendar.Items
            appointments.Sort("[Start]")
            appointments.IncludeRecurrences = True
            
            # Filter by date range
            appointments = appointments.Restrict(
                f"[Start] >= '{start_date.strftime('%m/%d/%Y')}' AND [Start] <= '{end_date.strftime('%m/%d/%Y')}'"
            )

            # Create events dictionary
            events = {}
            for appointment in appointments:
                date_str = appointment.Start.strftime('%Y-%m-%d')
                time_str = appointment.Start.strftime('%H:%M')
                
                if date_str not in events:
                    events[date_str] = []
                    
                event = {
                    'time': time_str,
                    'description': appointment.Subject,
                    'location': appointment.Location if appointment.Location else 'No location',
                    'duration': appointment.Duration,
                    'is_recurring': appointment.RecurrenceState != 0
                }
                events[date_str].append(event)

            # Save to cache
            cache_data = {
                'last_sync': datetime.now().isoformat(),
                'events': events
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=4)

            return events

        except Exception as e:
            trace_exception(e)
            return None

    def get_events_for_date(self, date_str):
        try:
            if self.needs_sync():
                self.sync_with_outlook()
                
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
                return cache_data['events'].get(date_str, [])
        except:
            return []

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        # Get current date if not specified in parameters
        date = datetime.now()

        # Get events for the specified date
        events = self.get_events_for_date(date)

        # Add agenda information to context
        agenda_context = f"\nOutlook Calendar for {date}:\n"
        if events:
            for event in events:
                agenda_context += f"- {event['time']}: {event['description']} "
                if event['location'] != 'No location':
                    agenda_context += f"@ {event['location']} "
                agenda_context += f"({event['duration']} minutes)"
                if event['is_recurring']:
                    agenda_context += " (Recurring)"
                agenda_context += "\n"
        else:
            agenda_context += "No events scheduled for this date.\n"

        constructed_context.append(agenda_context)
        return constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        return llm_output