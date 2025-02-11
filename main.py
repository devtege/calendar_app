import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
from datetime import datetime, timedelta
import json
import os

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calendar App")
        self.current_date = datetime.now()
        self.events = {}
        self.selected_day = None
        self.load_events()
        
        # Configure main window layout
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f2f5")  # Modern background color
        
        # Make the window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container with modern styling
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Make calendar grid expandable
        
        # Configure modern styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Modern styling configurations
        self.style.configure("Header.TLabel", 
                           font=('Helvetica', 14, 'bold'),
                           background="#ffffff",
                           padding=10)
        
        self.style.configure("Calendar.TFrame",
                           background="#ffffff",
                           relief="flat")
        
        self.style.configure("DayCell.TFrame",
                           background="#ffffff",
                           relief="flat",
                           borderwidth=1)
        
        self.style.configure("Selected.TFrame",
                           background="#e3f2fd",
                           relief="solid",
                           borderwidth=2)
        
        self.style.configure("Today.TLabel",
                           background="#bbdefb",
                           font=('Helvetica', 10, 'bold'))
        
        self.style.configure("DayHeader.TLabel",
                           font=('Helvetica', 10, 'bold'),
                           padding=10,
                           background="#ffffff")
        
        self.style.configure("NavButton.TButton",
                           font=('Helvetica', 12),
                           padding=5)
        
        # Create calendar widgets
        self.create_header()
        self.create_calendar_grid()
        self.create_event_panel()
        
        self.update_calendar()

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame, style="Calendar.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.month_year_label = ttk.Label(header_frame, 
                                        style="Header.TLabel",
                                        anchor="center")
        self.month_year_label.grid(row=0, column=1, sticky="ew")
        
        ttk.Button(header_frame, 
                  text="◀",
                  command=self.previous_month,
                  style="NavButton.TButton").grid(row=0, column=0, padx=5)
        
        ttk.Button(header_frame,
                  text="▶",
                  command=self.next_month,
                  style="NavButton.TButton").grid(row=0, column=2, padx=5)

    def create_calendar_grid(self):
        self.calendar_frame = ttk.Frame(self.main_frame, style="Calendar.TFrame")
        self.calendar_frame.grid(row=1, column=0, sticky="nsew")
        
        # Configure grid layout to fill space
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(7):  # 6 rows for days + 1 row for headers
            self.calendar_frame.grid_rowconfigure(i, weight=1)
        
        # Create day headers with modern styling
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ttk.Label(self.calendar_frame,
                     text=day,
                     style="DayHeader.TLabel",
                     anchor="center").grid(row=0, column=i, sticky="nsew")

    def create_event_panel(self):
        event_frame = ttk.Frame(self.main_frame, style="Calendar.TFrame")
        event_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        event_frame.grid_columnconfigure(0, weight=1)
        
        # Modern listbox styling
        self.event_listbox = tk.Listbox(event_frame,
                                      height=8,
                                      font=('Helvetica', 11),
                                      selectmode=tk.SINGLE,
                                      relief="flat",
                                      bg="#ffffff",
                                      selectbackground="#bbdefb",
                                      selectforeground="#000000")
        self.event_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(event_frame,
                                orient="vertical",
                                command=self.event_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.event_listbox.config(yscrollcommand=scrollbar.set)
        
        button_frame = ttk.Frame(event_frame, style="Calendar.TFrame")
        button_frame.pack(side="bottom", fill="x", pady=10)
        
        ttk.Button(button_frame,
                  text="Add Event",
                  command=self.add_event_dialog).pack(side="left", padx=5)
        ttk.Button(button_frame,
                  text="Delete Event",
                  command=self.delete_event).pack(side="left", padx=5)

    def update_calendar(self):
        # Clear previous calendar
        for widget in self.calendar_frame.winfo_children()[7:]:
            widget.destroy()
        
        # Update month/year display
        self.month_year_label.config(text=self.current_date.strftime("%B %Y"))
        
        # Calculate calendar dates
        first_day = self.current_date.replace(day=1)
        start_day = (first_day.weekday()) % 7
        days_in_month = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Calculate the number of weeks needed
        total_days = start_day + days_in_month.day
        num_weeks = (total_days + 6) // 7  # Round up to complete weeks
        
        # Ensure we have enough row configurations
        for i in range(num_weeks + 1):  # +1 for the header row
            self.calendar_frame.grid_rowconfigure(i, weight=1)
        
        # Create day cells
        row, col = 1, start_day
        for day in range(1, days_in_month.day + 1):
            day_frame = ttk.Frame(self.calendar_frame, style="DayCell.TFrame")
            day_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
            day_frame.grid_columnconfigure(0, weight=1)
            day_frame.grid_rowconfigure(0, weight=1)
            
            # Create day content frame to hold label and event indicator
            content_frame = ttk.Frame(day_frame)
            content_frame.grid(row=0, column=0, sticky="nsew")
            content_frame.grid_columnconfigure(0, weight=1)
            
            # Day label
            day_label = ttk.Label(content_frame,
                                text=str(day),
                                anchor="center",
                                padding=10)
            day_label.grid(row=0, column=0, sticky="nsew")
            
            # Event indicator
            date_str = self.current_date.replace(day=day).strftime("%Y-%m-%d")
            if date_str in self.events and self.events[date_str]:
                indicator = tk.Frame(content_frame,
                                  bg=self.events[date_str][0]['color'],
                                  height=4)
                indicator.grid(row=1, column=0, sticky="ew")
            
            # Highlight today
            if (self.current_date.year == datetime.now().year and
                self.current_date.month == datetime.now().month and
                day == datetime.now().day):
                day_label.config(style="Today.TLabel")
            
            # Store the day number
            day_frame.day_number = day
            content_frame.day_number = day
            day_label.day_number = day
            
            # Bind click events
            day_frame.bind("<Button-1>", self.handle_day_click)
            content_frame.bind("<Button-1>", self.handle_day_click)
            day_label.bind("<Button-1>", self.handle_day_click)
            
            # Update grid position
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        # Fill remaining cells with empty frames to maintain grid structure
        while col <= 6:
            empty_frame = ttk.Frame(self.calendar_frame, style="DayCell.TFrame")
            empty_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
            col += 1
    
    def handle_day_click(self, event):
        # Get the clicked widget and find its day number
        widget = event.widget
        day = getattr(widget, 'day_number', None)
        
        if day is None:
            # Try to get day from parent if it's a child widget
            day = getattr(widget.master, 'day_number', None)
        
        if day is not None:
            # Find the day frame (it's either the widget or its parent)
            frame = widget
            while frame and not isinstance(frame, ttk.Frame):
                frame = frame.master
                
            if frame and hasattr(frame, 'day_number'):
                self.select_day(day, frame)

    def select_day(self, day, day_frame):
        # Reset previous selection without disturbing the grid
        if self.selected_day:
            try:
                # Find the actual day frame if we're dealing with a child widget
                prev_frame = self.selected_day
                if not isinstance(prev_frame, ttk.Frame):
                    prev_frame = prev_frame.master
                prev_frame.configure(style="DayCell.TFrame")
            except tk.TclError:
                pass  # Handle case where previous frame was destroyed
        
        # Find the actual day frame if we're dealing with a child widget
        actual_day_frame = day_frame
        if not isinstance(day_frame, ttk.Frame):
            actual_day_frame = day_frame.master
            
        # Apply selection styling without modifying grid structure
        actual_day_frame.configure(style="Selected.TFrame")
        self.selected_day = actual_day_frame
        
        # Set selected date and update events display
        self.selected_date = self.current_date.replace(day=day).strftime("%Y-%m-%d")
        self.show_events(day)

    def previous_month(self):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.update_calendar()

    def next_month(self):
        self.current_date = self.current_date.replace(day=28) + timedelta(days=4)
        self.current_date = self.current_date.replace(day=1)
        self.update_calendar()

    def show_events(self, day):
        selected_date = self.current_date.replace(day=day).strftime("%Y-%m-%d")
        self.selected_date = selected_date
        self.event_listbox.delete(0, tk.END)
        
        if selected_date in self.events:
            for event in sorted(self.events[selected_date], key=lambda x: x['time']):
                self.event_listbox.insert(tk.END, f"{event['time']} - {event['description']}")

    def add_event_dialog(self):
        if not hasattr(self, 'selected_date'):
            messagebox.showwarning("No Date Selected", "Please select a date first!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Event")
        dialog.geometry("300x200")
        dialog.configure(bg="#ffffff")
        
        selected_color = "#4a90e2"  # Modern blue as default
        
        def choose_color():
            nonlocal selected_color
            color = colorchooser.askcolor(title="Choose Color", color=selected_color)
            if color[1]:
                selected_color = color[1]
                color_preview.config(bg=selected_color)
        
        ttk.Label(dialog, text="Time (HH:MM):", background="#ffffff").pack(pady=5)
        time_entry = ttk.Entry(dialog)
        time_entry.pack()
        
        ttk.Label(dialog, text="Description:", background="#ffffff").pack(pady=5)
        desc_entry = ttk.Entry(dialog)
        desc_entry.pack()
        
        color_frame = ttk.Frame(dialog)
        color_frame.pack(pady=5)
        ttk.Button(color_frame, text="Choose Color", command=choose_color).pack(side="left", padx=5)
        color_preview = tk.Frame(color_frame, width=20, height=20, bg=selected_color, relief="solid", borderwidth=1)
        color_preview.pack(side="left")
        
        def save_event():
            time = time_entry.get()
            description = desc_entry.get()
            if self.validate_time(time):
                self.add_event(time, description, selected_color)
                dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_event).pack(pady=10)

    def validate_time(self, time_str):
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            messagebox.showerror("Invalid Time", "Please use HH:MM format (e.g., 14:30)")
            return False

    def add_event(self, time, description, color):
        event = {"time": time, "description": description, "color": color}
        if self.selected_date not in self.events:
            self.events[self.selected_date] = []
        self.events[self.selected_date].append(event)
        self.events[self.selected_date].sort(key=lambda x: datetime.strptime(x['time'], "%H:%M"))
        self.show_events(int(self.selected_date.split("-")[2]))
        self.save_events()
        self.update_calendar()

    def delete_event(self):
        selection = self.event_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        del self.events[self.selected_date][index]
        if not self.events[self.selected_date]:
            del self.events[self.selected_date]
        self.show_events(int(self.selected_date.split("-")[2]))
        self.save_events()
        self.update_calendar()

    def save_events(self):
        with open("calendar_events.json", "w") as f:
            json.dump(self.events, f)

    def load_events(self):
        if os.path.exists("calendar_events.json"):
            with open("calendar_events.json", "r") as f:
                self.events = json.load(f)
            # Add color field to existing events
            for date_str in self.events:
                for event in self.events[date_str]:
                    if 'color' not in event:
                        event['color'] = "#4a90e2"  # Modern blue as default
        else:
            self.events = {}

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
