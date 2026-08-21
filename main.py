from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

from datetime import datetime
import json
import os


DATA_FILE = "medicines.json"


class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.medicines = []
        self.load_data()

        main_layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )

        title = Label(
            text="MEDICINE REMINDER",
            font_size=30,
            size_hint_y=None,
            height=60
        )

        self.medicine_list = BoxLayout(
            orientation="vertical",
            spacing=8
        )

        add_button = Button(
            text="+ ADD MEDICINE",
            font_size=18,
            size_hint_y=None,
            height=55
        )

        history_button = Button(
            text="VIEW HISTORY",
            font_size=18,
            size_hint_y=None,
            height=50
        )

        test_button = Button(
            text="TEST REMINDER",
            font_size=18,
            size_hint_y=None,
            height=50
        )

        add_button.bind(
            on_press=self.open_add
        )

        history_button.bind(
            on_press=self.open_history
        )

        test_button.bind(
            on_press=self.test_reminder
        )

        main_layout.add_widget(title)
        main_layout.add_widget(self.medicine_list)
        main_layout.add_widget(add_button)
        main_layout.add_widget(history_button)
        main_layout.add_widget(test_button)

        self.add_widget(main_layout)

        self.refresh_list()

        Clock.schedule_interval(
            self.check_reminders,
            1
        )

    # SAVE DATA

    def save_data(self):

        with open(DATA_FILE, "w") as file:
            json.dump(
                self.medicines,
                file,
                indent=4
            )

    # LOAD DATA

    def load_data(self):

        if os.path.exists(DATA_FILE):

            try:

                with open(DATA_FILE, "r") as file:
                    self.medicines = json.load(file)

            except:
                self.medicines = []

    # ADD MEDICINE

    def add_medicine(self, name, dosage, time):

        medicine = {
            "name": name,
            "dosage": dosage,
            "time": time,
            "taken": False,
            "last_reminded": ""
        }

        self.medicines.append(medicine)

        self.save_data()
        self.refresh_list()

    # DISPLAY MEDICINES

    def refresh_list(self):

        self.medicine_list.clear_widgets()

        if not self.medicines:

            self.medicine_list.add_widget(
                Label(
                    text="No medicines added yet.",
                    font_size=18
                )
            )

            return

        for medicine in self.medicines:

            row = BoxLayout(
                orientation="vertical",
                spacing=5,
                size_hint_y=None,
                height=130
            )

            info = Label(
                text=(
                    "💊 " + medicine["name"]
                    + "\nDosage: " + medicine["dosage"]
                    + "\nTime: " + medicine["time"]
                ),
                font_size=16
            )

            buttons = BoxLayout(
                orientation="horizontal",
                spacing=5,
                size_hint_y=None,
                height=45
            )

            edit_button = Button(
                text="EDIT"
            )

            delete_button = Button(
                text="DELETE"
            )

            taken_button = Button(
                text="TAKEN"
            )

            edit_button.bind(
                on_press=lambda instance, med=medicine:
                self.edit_medicine(med)
            )

            delete_button.bind(
                on_press=lambda instance, med=medicine:
                self.delete_medicine(med)
            )

            taken_button.bind(
                on_press=lambda instance, med=medicine:
                self.mark_taken(med)
            )

            buttons.add_widget(edit_button)
            buttons.add_widget(delete_button)
            buttons.add_widget(taken_button)

            row.add_widget(info)
            row.add_widget(buttons)

            self.medicine_list.add_widget(row)

    # DELETE

    def delete_medicine(self, medicine):

        if medicine in self.medicines:

            self.medicines.remove(medicine)

            self.save_data()
            self.refresh_list()

    # EDIT

    def edit_medicine(self, medicine):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        name_input = TextInput(
            text=medicine["name"],
            multiline=False
        )

        dosage_input = TextInput(
            text=medicine["dosage"],
            multiline=False
        )

        time_input = TextInput(
            text=medicine["time"],
            multiline=False
        )

        save_button = Button(
            text="SAVE CHANGES"
        )

        content.add_widget(
            Label(text="Medicine Name")
        )

        content.add_widget(name_input)

        content.add_widget(
            Label(text="Dosage")
        )

        content.add_widget(dosage_input)

        content.add_widget(
            Label(text="Time")
        )

        content.add_widget(time_input)

        content.add_widget(save_button)

        popup = Popup(
            title="EDIT MEDICINE",
            content=content,
            size_hint=(0.9, 0.8)
        )

        def save_changes(instance):

            medicine["name"] = name_input.text
            medicine["dosage"] = dosage_input.text
            medicine["time"] = time_input.text

            medicine["taken"] = False
            medicine["last_reminded"] = ""

            self.save_data()
            self.refresh_list()

            popup.dismiss()

        save_button.bind(
            on_press=save_changes
        )

        popup.open()

    # MARK AS TAKEN

    def mark_taken(self, medicine):

        medicine["taken"] = True

        self.save_data()
        self.refresh_list()

        self.show_popup(
            "Medicine Taken",
            medicine["name"]
            + "\nMarked as taken! ✅"
        )

    # CONVERT TIME

    def convert_time(self, time_text):

        time_text = time_text.strip().upper()

        formats = [
            "%H:%M",
            "%I:%M %p",
            "%I:%M%p"
        ]

        for fmt in formats:

            try:

                result = datetime.strptime(
                    time_text,
                    fmt
                )

                return result.strftime("%H:%M")

            except ValueError:
                pass

        return None

    # AUTOMATIC REMINDER
    # THIS NOW SUPPORTS MULTIPLE
    # MEDICINES AT THE SAME TIME

    def check_reminders(self, dt):

        now = datetime.now()

        current_time = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")

        medicines_due = []

        for medicine in self.medicines:

            medicine_time = self.convert_time(
                medicine["time"]
            )

            if medicine_time == current_time:

                reminder_id = (
                    today
                    + current_time
                    + medicine["name"]
                )

                if medicine["last_reminded"] != reminder_id:

                    medicines_due.append(medicine)

                    medicine["last_reminded"] = reminder_id

        if medicines_due:

            self.save_data()

            message = "🔔 TIME FOR MEDICINE!\n\n"

            for medicine in medicines_due:

                message += (
                    "💊 "
                    + medicine["name"]
                    + "\nDosage: "
                    + medicine["dosage"]
                    + "\n\n"
                )

            self.show_popup(
                "MEDICINE REMINDER",
                message
            )

    # POPUP

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(
            text=message,
            font_size=19
        )

        ok_button = Button(
            text="OK",
            size_hint_y=None,
            height=50
        )

        content.add_widget(label)
        content.add_widget(ok_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.55),
            auto_dismiss=False
        )

        ok_button.bind(
            on_press=popup.dismiss
        )

        popup.open()

    # TEST REMINDER

    def test_reminder(self, instance):

        if self.medicines:

            medicine = self.medicines[0]

            self.show_popup(
                "🔔 TEST REMINDER",
                "Time to take:\n\n"
                + medicine["name"]
                + "\n"
                + medicine["dosage"]
            )

        else:

            self.show_popup(
                "🔔 TEST REMINDER",
                "This is a test reminder!"
            )

    # OPEN ADD SCREEN

    def open_add(self, instance):

        self.manager.current = "add"

    # OPEN HISTORY

    def open_history(self, instance):

        self.manager.current = "history"


class AddMedicineScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="ADD MEDICINE",
            font_size=28
        )

        self.name_input = TextInput(
            hint_text="Enter medicine name",
            multiline=False
        )

        self.dosage_input = TextInput(
            hint_text="Enter dosage",
            multiline=False
        )

        self.time_input = TextInput(
            hint_text="Enter time e.g. 13:30",
            multiline=False
        )

        save_button = Button(
            text="SAVE MEDICINE",
            font_size=20
        )

        back_button = Button(
            text="BACK"
        )

        save_button.bind(
            on_press=self.save_medicine
        )

        back_button.bind(
            on_press=self.go_back
        )

        layout.add_widget(title)
        layout.add_widget(self.name_input)
        layout.add_widget(self.dosage_input)
        layout.add_widget(self.time_input)
        layout.add_widget(save_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def save_medicine(self, instance):

        name = self.name_input.text.strip()
        dosage = self.dosage_input.text.strip()
        time = self.time_input.text.strip()

        if name and dosage and time:

            home = self.manager.get_screen("home")

            home.add_medicine(
                name,
                dosage,
                time
            )

            self.name_input.text = ""
            self.dosage_input.text = ""
            self.time_input.text = ""

            self.manager.current = "home"

    def go_back(self, instance):

        self.manager.current = "home"


class HistoryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="MEDICINE HISTORY",
            font_size=28
        )

        self.history_label = Label(
            text="History will appear here.",
            font_size=18
        )

        back_button = Button(
            text="BACK",
            size_hint_y=None,
            height=55
        )

        back_button.bind(
            on_press=self.go_back
        )

        layout.add_widget(title)
        layout.add_widget(self.history_label)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def on_enter(self):

        home = self.manager.get_screen("home")

        history = []

        for medicine in home.medicines:

            if medicine["taken"]:

                history.append(
                    "✅ "
                    + medicine["name"]
                    + " - "
                    + medicine["dosage"]
                )

        if history:

            self.history_label.text = "\n".join(history)

        else:

            self.history_label.text = (
                "No medicines marked as taken yet."
            )

    def go_back(self, instance):

        self.manager.current = "home"


class MedicineReminderApp(App):

    def build(self):

        manager = ScreenManager()

        manager.add_widget(
            HomeScreen(name="home")
        )

        manager.add_widget(
            AddMedicineScreen(name="add")
        )

        manager.add_widget(
            HistoryScreen(name="history")
        )

        return manager


MedicineReminderApp().run()
