# gui/event_details_panel.py
import tkinter as tk
from tkinter import ttk
from config import SCORE_LOW_COLOR, SCORE_MEDIUM_COLOR, SCORE_HIGH_COLOR

class EventDetailsPanel(ttk.Frame):
    """Displays details of a selected event."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator # Reference to the main app coordinator
        self.selected_event = None

        # --- UI Elements ---
        self.details_title = ttk.Label(self, text="Event Details", font=("Helvetica", 16, "bold"))
        self.details_title.pack(pady=10)

        # Variables for dynamic labels
        self.event_name_var = tk.StringVar(value="Select an event")
        self.event_desc_var = tk.StringVar(value="")
        self.event_score_var = tk.StringVar(value="Score: N/A")
        self.event_time_var = tk.StringVar(value="Time: N/A")
        self.event_location_var = tk.StringVar(value="Location: N/A")
        self.event_cost_var = tk.StringVar(value="Cost: N/A")

        ttk.Label(self, textvariable=self.event_name_var,
                 font=("Helvetica", 14)).pack(pady=5, anchor=tk.W, padx=10)
        ttk.Label(self, textvariable=self.event_desc_var,
                 wraplength=400, justify=tk.LEFT).pack(pady=5, anchor=tk.W, padx=10)

        details_frame = ttk.Frame(self)
        details_frame.pack(fill=tk.X, expand=False, pady=10, padx=10) # Don't expand vertically

        ttk.Label(details_frame, textvariable=self.event_score_var,
                 font=("Helvetica", 12, "bold")).pack(pady=5, anchor=tk.W)
        ttk.Label(details_frame, textvariable=self.event_time_var).pack(pady=2, anchor=tk.W)
        ttk.Label(details_frame, textvariable=self.event_location_var).pack(pady=2, anchor=tk.W)
        ttk.Label(details_frame, textvariable=self.event_cost_var).pack(pady=2, anchor=tk.W)

        # Score visualization canvas
        self.score_canvas = tk.Canvas(self, width=400, height=30, bg="white", highlightthickness=0)
        self.score_canvas.pack(pady=10, padx=10)
        self._draw_score_visualization(0) # Initial empty bar

        # Fuzzy scores breakdown
        score_frame = ttk.LabelFrame(self, text="Recommendation Factors (Scores: 0-100)")
        score_frame.pack(fill=tk.X, expand=False, padx=10, pady=10) # Don't expand vertically

        self.interest_score_var = tk.StringVar(value="Interest Match: N/A")
        self.location_score_var = tk.StringVar(value="Location Proximity: N/A")
        self.time_score_var = tk.StringVar(value="Time Overlap: N/A")
        self.budget_score_var = tk.StringVar(value="Budget Alignment: N/A")
        self.history_boost_var = tk.StringVar(value="History Boost: N/A") # Added

        ttk.Label(score_frame, textvariable=self.interest_score_var).pack(anchor=tk.W, pady=2)
        ttk.Label(score_frame, textvariable=self.location_score_var).pack(anchor=tk.W, pady=2)
        ttk.Label(score_frame, textvariable=self.time_score_var).pack(anchor=tk.W, pady=2)
        ttk.Label(score_frame, textvariable=self.budget_score_var).pack(anchor=tk.W, pady=2)
        ttk.Label(score_frame, textvariable=self.history_boost_var).pack(anchor=tk.W, pady=2)

        # Add to history button
        self.add_to_history_btn = ttk.Button(self, text="Attend (Add to History)",
                                            command=self._add_to_history)
        self.add_to_history_btn.pack(pady=10)
        self.add_to_history_btn.config(state=tk.DISABLED)

    def display_event_details(self, event):
        """Update the panel to show details for the given event."""
        self.selected_event = event
        if not event:
            self.clear_details()
            return

        self.event_name_var.set(event.name)
        self.event_desc_var.set(event.description)
        self.event_score_var.set(f"Recommendation Score: {event.recommendation_score:.1f}%")
        # Format time/location/cost...
        self.event_time_var.set(f"Time: {event.start_time.strftime('%a %I:%M %p')} - {event.end_time.strftime('%I:%M %p')}")
        self.event_location_var.set(f"Location: {event.latitude:.4f}, {event.longitude:.4f}")
        self.event_cost_var.set(f"Cost: ${event.cost:.2f}")


        # Update factor scores using the breakdown stored in the event
        scores = event.scores_breakdown
        # --- Check retrieval keys ---
        self.interest_score_var.set(f"Interest Match (Base): {scores.get('interest_match', 0):.1f}%") # Get base score
        self.location_score_var.set(f"Location Proximity: {scores.get('location_proximity', 0):.1f}%")
        self.time_score_var.set(f"Time Overlap: {scores.get('time_overlap', 0):.1f}%")
        self.budget_score_var.set(f"Budget Alignment: {scores.get('budget_alignment', 0):.1f}%")
        # Retrieve the stored boost value
        boost_val = scores.get('history_boost', 0)
        self.history_boost_var.set(f"History Boost Applied: +{boost_val:.1f}%") # Use the 'history_boost' key
        # --- End Check ---

        # Draw score visualization
        self._draw_score_visualization(event.recommendation_score)

        # Enable add to history button
        self.add_to_history_btn.config(state=tk.NORMAL)

    def clear_details(self):
        """Clear the event details display."""
        # ... (rest of clear_details is likely okay) ...
        self.interest_score_var.set("Interest Match (Base): N/A") # Update label text
        self.location_score_var.set("Location Proximity: N/A")
        self.time_score_var.set("Time Overlap: N/A")
        self.budget_score_var.set("Budget Alignment: N/A")
        self.history_boost_var.set("History Boost Applied: N/A") # Clear boost display

        self._draw_score_visualization(0) # Clear score bar
        self.add_to_history_btn.config(state=tk.DISABLED)

    def _draw_score_visualization(self, score):
        """Draw a visual representation of the recommendation score."""
        self.score_canvas.delete("all")

        # Draw background
        canvas_width = self.score_canvas.winfo_width() # Use actual width
        if canvas_width <= 1: canvas_width = 400 # Default if not realized yet
        self.score_canvas.create_rectangle(0, 0, canvas_width, 30, fill="lightgray", outline="")

        # Draw score bar
        bar_width = int(score * (canvas_width / 100.0))
        bar_width = max(0, min(canvas_width, bar_width)) # Clamp width


        # Color gradient based on score
        if score < 30: color = SCORE_LOW_COLOR
        elif score < 70: color = SCORE_MEDIUM_COLOR
        else: color = SCORE_HIGH_COLOR

        if bar_width > 0:
            self.score_canvas.create_rectangle(0, 0, bar_width, 30, fill=color, outline="")

        # Draw score text centered
        self.score_canvas.create_text(canvas_width / 2, 15, text=f"{score:.1f}%",
                                     font=("Helvetica", 12, "bold"))

    def _add_to_history(self):
        """Callback when 'Add to History' button is pressed."""
        if self.selected_event:
            self.app.request_add_to_history(self.selected_event)