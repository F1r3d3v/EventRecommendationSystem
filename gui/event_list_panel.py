import tkinter as tk
from tkinter import ttk
from config import SCORE_HIGH_COLOR, SCORE_HIGH_THRESHOLD, SCORE_LOW_COLOR, SCORE_MEDIUM_COLOR, SCORE_MEDIUM_THRESHOLD

class EventListPanel(ttk.Frame):
    """Panel for displaying event list with recommendations."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator
        self.displayed_events = []

        # --- UI Elements ---
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(controls_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="Recommendation")
        sort_options = ["Recommendation", "Name", "Time", "Cost", "Distance"]
        sort_combo = ttk.Combobox(controls_frame, textvariable=self.sort_var,
                                values=sort_options, width=15, state="readonly")
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.app.refresh_recommendations())

        ttk.Label(controls_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind("<KeyRelease>", lambda e: self.app.refresh_recommendations())

        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.event_listbox = tk.Listbox(list_frame, font=("Helvetica", 11), selectmode=tk.SINGLE)
        self.event_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.event_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.event_listbox.config(yscrollcommand=scrollbar.set)

        self.event_listbox.bind("<<ListboxSelect>>", self._on_event_select)


    def get_sort_key(self):
        """Returns the currently selected sort key."""
        return self.sort_var.get()


    def get_search_term(self):
        """Returns the current search term."""
        return self.search_var.get()


    def display_events(self, events):
        """Populates the listbox with the given list of events."""
        self.event_listbox.delete(0, tk.END)
        self.displayed_events = events

        for i, event in enumerate(events):
            text = f"{event.name} ({event.recommendation_score:.1f}%) - {event.category}"
            self.event_listbox.insert(tk.END, text)

            # Color coding based on score using config thresholds
            if event.recommendation_score >= SCORE_HIGH_THRESHOLD:
                self.event_listbox.itemconfig(i, {'bg': SCORE_HIGH_COLOR})
            elif event.recommendation_score >= SCORE_MEDIUM_THRESHOLD:
                self.event_listbox.itemconfig(i, {'bg': SCORE_MEDIUM_COLOR})
            else:
                self.event_listbox.itemconfig(i, {'bg': SCORE_LOW_COLOR})


    def select_first(self):
        """Selects the first item in the list if available."""
        if self.event_listbox.size() > 0:
            self.event_listbox.selection_set(0)
            self.event_listbox.activate(0)
            self.event_listbox.see(0)
            self._on_event_select(None)


    def _on_event_select(self, event_unused):
        """Handles event selection in the listbox and notifies the app."""
        selected_indices = self.event_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            if 0 <= index < len(self.displayed_events):
                selected_event = self.displayed_events[index]
                self.app.event_selected(selected_event)
        else:
             self.app.event_selected(None)


    def get_selected_event(self):
        """Gets the currently selected event object."""
        selected_indices = self.event_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            if 0 <= index < len(self.displayed_events):
                return self.displayed_events[index]
        return None
