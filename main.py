import re  # Regular expressions for input validation
import datetime
import requests
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty, NumericProperty

# Replace this with your ngrok URL or localhost for testing
API_BASE_URL = "https://0876-197-210-85-207.ngrok-free.app"

KV = '''
<ModernCard>:
    orientation: 'vertical'
    padding: '16dp'
    size_hint: None, None
    size: "280dp", "220dp"
    radius: 12
    elevation: 2
    md_bg_color: app.theme_cls.bg_normal
    ripple_behavior: True

    MDBoxLayout:
        orientation: 'vertical'
        spacing: '8dp'

        MDLabel:
            text: root.user_text
            font_style: "H6"
            theme_text_color: "Primary"
            adaptive_height: True
            bold: True

        MDLabel:
            text: root.time_text
            font_style: "Body1"
            theme_text_color: "Secondary"
            adaptive_height: True

        MDLabel:
            text: root.scripture_text
            font_style: "Body1"
            theme_text_color: "Secondary"
            adaptive_height: True
            markup: True

        MDBoxLayout:
            orientation: 'horizontal'
            adaptive_size: True
            spacing: '8dp'
            pos_hint: {'center_x': 0.5}

            MDRoundFlatIconButton:
                icon: "calendar-plus"
                text: "Add to Calendar"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_color
                on_release: root.add_to_calendar()

            MDIconButton:
                icon: "delete"
                theme_icon_color: "Error"
                on_release: root.delete_reminder()

MDScreen:
    MDNavigationLayout:
        MDScreenManager:
            id: screen_manager

            MDScreen:
                name: "main"

                MDBoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        title: "Prayer Reminder"
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                        right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]
                        elevation: 4

                    ScrollView:
                        MDGridLayout:
                            id: main_layout
                            cols: 1
                            adaptive_height: True
                            padding: "20dp"
                            spacing: "20dp"

                            MDBoxLayout:
                                orientation: 'vertical'
                                spacing: '16dp'
                                adaptive_height: True

                                MDTextField:
                                    id: name_field
                                    hint_text: "Reminder Title"
                                    fill_color_normal: app.theme_cls.bg_normal
                                    icon_right: "text"

                                MDTextField:
                                    id: time_field
                                    hint_text: "Select Time"
                                    fill_color_normal: app.theme_cls.bg_normal
                                    icon_right: "clock-outline"
                                    on_focus: if self.focus: app.time_menu.open()

                                MDTextField:
                                    id: scripture_field
                                    hint_text: "Scripture Reference"
                                    fill_color_normal: app.theme_cls.bg_normal
                                    icon_right: "book-open-page-variant"

                                MDRaisedButton:
                                    icon: "plus"
                                    text: "Add Reminder"
                                    pos_hint: {'center_x': 0.5}
                                    on_release: app.add_reminder()

                            MDGridLayout:
                                id: cards_container
                                cols: 2 if self.width > dp(600) else 1
                                adaptive_height: True
                                spacing: "20dp"

                    MDFloatingActionButton:
                        icon: "refresh"
                        pos_hint: {'right': 0.98, 'bottom': 0.98}
                        elevation: 6
                        on_release: app.list_reminders()

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)

            MDBoxLayout:
                orientation: 'vertical'
                spacing: "8dp"
                padding: "8dp"

                MDLabel:
                    text: "Menu"
                    font_style: "H5"
                    halign: "center"
                    size_hint_y: None
                    height: self.texture_size[1]

                ScrollView:
                    MDList:
                        OneLineIconListItem:
                            text: "Settings"
                            IconLeftWidget:
                                icon: "cog"

                        OneLineIconListItem:
                            text: "About"
                            IconLeftWidget:
                                icon: "information"

                        OneLineIconListItem:
                            text: "Exit"
                            IconLeftWidget:
                                icon: "exit-to-app"
'''

class ModernCard(MDCard, RectangularRippleBehavior):
    user_text = StringProperty()
    time_text = StringProperty()
    scripture_text = StringProperty()
    reminder_id = NumericProperty()  # <<-- NEW: store the unique ID

    def __init__(self, user, time, scripture, last_triggered, reminder_id, **kwargs):
        super().__init__(**kwargs)
        self.user_text = user
        self.time_text = time
        self.scripture_text = scripture
        self.last_triggered = last_triggered
        self.reminder_id = reminder_id

    def add_to_calendar(self):
        MDApp.get_running_app().add_to_calendar({
            "user": self.user_text,
            "time": self.time_text,
            "scripture": self.scripture_text
        })

    def delete_reminder(self):
        # Instead of passing the user name, we pass the ID
        MDApp.get_running_app().delete_reminder(self.reminder_id)

class PrayerReminderApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        
        self.screen = Builder.load_string(KV)
        self.time_menu = self.create_time_menu()
        return self.screen

    def toggle_theme(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def create_time_menu(self):
        time_items = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 15)]
        menu_items = [
            {
                "text": time,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=time: self.set_time(x),
            } for time in time_items
        ]
        return MDDropdownMenu(
            caller=self.screen.ids.time_field,
            items=menu_items,
            position="bottom",
            size_hint=(None, None),
            width=dp(200),
        )

    def set_time(self, time):
        self.screen.ids.time_field.text = time
        self.time_menu.dismiss()

    def validate_inputs(self):
        # Validate time
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", self.screen.ids.time_field.text):
            self.show_dialog("Invalid Time", "Please use HH:MM format (24-hour)")
            return False
        
        # Validate scripture
        scripture = self.screen.ids.scripture_field.text
        if not re.match(r"^[A-Za-z]+\s\d+:\d+(-\d+)?$", scripture):
            self.show_dialog("Invalid Scripture", "Use format: Book Chapter:Verse (e.g. John 3:16)")
            return False
        
        return True

    def add_reminder(self):
        if not self.validate_inputs():
            return

        data = {
            "user": self.screen.ids.name_field.text,
            "time": self.screen.ids.time_field.text,
            "scripture": self.screen.ids.scripture_field.text
        }

        try:
            response = requests.post(f"{API_BASE_URL}/add_reminder", json=data)
            if response.status_code == 201:
                self.list_reminders()
                self.clear_inputs()
            else:
                self.show_dialog("Error", f"Failed to add reminder: {response.text}")
        except Exception as e:
            self.show_dialog("Connection Error", str(e))

    def list_reminders(self):
        try:
            response = requests.get(f"{API_BASE_URL}/reminders")
            if response.status_code == 200:
                self.screen.ids.cards_container.clear_widgets()
                for reminder in response.json():
                    # Pass the 'id' from the JSON to the card
                    card = ModernCard(
                        user=reminder["user"],
                        time=self.format_time(reminder["time"]),
                        scripture=reminder["scripture"],
                        last_triggered=reminder.get("last_triggered_date", "Never"),
                        reminder_id=reminder["id"]  # <--- KEY CHANGE
                    )
                    self.screen.ids.cards_container.add_widget(card)
            else:
                self.show_dialog("Error", f"Failed to load reminders: {response.text}")
        except Exception as e:
            self.show_dialog("Connection Error", str(e))

    def format_time(self, time_str):
        try:
            return datetime.datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        except:
            return time_str

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def clear_inputs(self):
        self.screen.ids.name_field.text = ""
        self.screen.ids.time_field.text = ""
        self.screen.ids.scripture_field.text = ""

    def delete_reminder(self, reminder_id):
        """
        Deletes a reminder by its integer ID (instead of user name).
        """
        try:
            response = requests.delete(f"{API_BASE_URL}/reminder/{reminder_id}")
            if response.status_code == 200:
                self.list_reminders()
            else:
                self.show_dialog("Error", f"Failed to delete reminder: {response.text}")
        except Exception as e:
            self.show_dialog("Connection Error", str(e))

    def add_to_calendar(self, reminder):
        if platform != "android":
            self.show_dialog("Info", "Calendar integration is only supported on Android")
            return

        try:
            from jnius import autoclass, cast
            from android import activity
            from android.permissions import request_permissions, Permission

            # Request necessary permissions
            request_permissions([Permission.READ_CALENDAR, Permission.WRITE_CALENDAR])

            Calendar = autoclass('android.provider.CalendarContract$Events')
            CalendarContract = autoclass('android.provider.CalendarContract')
            ContentValues = autoclass('android.content.ContentValues')
            Uri = autoclass('android.net.Uri')
            context = cast('android.content.Context', activity.getApplicationContext())

            # Get the content resolver
            content_resolver = context.getContentResolver()

            # Create event values
            event_values = ContentValues()
            event_values.put(Calendar.TITLE, reminder["user"])
            event_values.put(Calendar.DESCRIPTION, reminder["scripture"])
            event_values.put(Calendar.DTSTART, self.get_time_in_millis(reminder["time"]))
            event_values.put(Calendar.DTEND, self.get_time_in_millis(reminder["time"]) + 60 * 60 * 1000)  # 1 hour duration
            event_values.put(Calendar.CALENDAR_ID, 1)
            event_values.put(Calendar.EVENT_TIMEZONE, 'UTC')

            # Insert the event
            uri = content_resolver.insert(Uri.parse("content://com.android.calendar/events"), event_values)

            # Set an alarm for the event
            Reminders = autoclass('android.provider.CalendarContract$Reminders')
            reminder_values = ContentValues()
            reminder_values.put(Reminders.EVENT_ID, int(uri.getLastPathSegment()))
            reminder_values.put(Reminders.METHOD, Reminders.METHOD_ALERT)
            reminder_values.put(Reminders.MINUTES, 10)  # 10 minutes before

            content_resolver.insert(Uri.parse("content://com.android.calendar/reminders"), reminder_values)

            self.show_dialog("Success", "Reminder added to calendar with alarm")
        except Exception as e:
            self.show_dialog("Error", f"Calendar error: {str(e)}")

    def get_time_in_millis(self, time_str):
        now = datetime.datetime.now()
        reminder_time = datetime.datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        if reminder_time < now:
            reminder_time += datetime.timedelta(days=1)  # If time has passed for today, schedule next day
        return int(reminder_time.timestamp() * 1000)


if __name__ == '__main__':
    PrayerReminderApp().run()
