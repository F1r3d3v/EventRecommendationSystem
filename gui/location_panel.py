import os
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.image as mpimg
from matplotlib.patches import Ellipse
import numpy as np
from config import (
    DEFAULT_MAX_DISTANCE, MAP_LAT_LIMITS, MAP_LON_LIMITS, ROOT_DIR
)

class LocationPanel(ttk.Frame):
    """Panel for setting location preferences."""
    def __init__(self, parent, app_coordinator):
        super().__init__(parent)
        self.app = app_coordinator

        # Get initial preferences
        prefs = self.app.get_current_preferences()
        initial_lat = prefs.location['latitude']
        initial_lon = prefs.location['longitude']
        initial_distance = prefs.max_distance

        # --- UI Elements ---
        map_frame = ttk.LabelFrame(self, text="Select Your Location (Click on Map)")
        map_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Calculate aspect ratio based on map coordinates
        map_width = MAP_LON_LIMITS[1] - MAP_LON_LIMITS[0]
        map_height = MAP_LAT_LIMITS[1] - MAP_LAT_LIMITS[0]
        aspect_ratio = map_width / map_height
        
        # Create a figure
        self.fig, self.ax = plt.subplots(figsize=(8, 8/aspect_ratio))
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)
        self._setup_map()
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.fig.canvas.mpl_connect('button_press_event', self._on_map_click)
        self.user_marker = None
        self.radius_circle = None
        self.event_markers = []

        # Coordinates Input
        coords_frame = ttk.Frame(self)
        coords_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        ttk.Label(coords_frame, text="Latitude:").grid(row=0, column=0, padx=5, pady=2)
        self.lat_var = tk.DoubleVar(value=initial_lat)
        self.lat_entry = ttk.Entry(coords_frame, textvariable=self.lat_var, width=10)
        self.lat_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(coords_frame, text="Longitude:").grid(row=0, column=2, padx=(10, 5), pady=2)
        self.lon_var = tk.DoubleVar(value=initial_lon)
        self.lon_entry = ttk.Entry(coords_frame, textvariable=self.lon_var, width=10)
        self.lon_entry.grid(row=0, column=3, padx=5, pady=2)

        # Bind Enter key in entries to update location
        self.lat_entry.bind("<Return>", self._update_location_from_inputs)
        self.lon_entry.bind("<Return>", self._update_location_from_inputs)

        ttk.Button(coords_frame, text="Set Location", command=self._update_location_from_inputs).grid(
            row=0, column=4, padx=(10, 5), pady=2)

        # Max Distance Slider
        distance_frame = ttk.LabelFrame(self, text="Maximum Search Distance")
        distance_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.distance_var = tk.IntVar(value=initial_distance)
        self.distance_label = ttk.Label(distance_frame, text=f"{initial_distance} km", width=8, anchor=tk.E)
        self.distance_label.pack(side=tk.RIGHT, padx=(5, 10), pady=5)

        self.distance_slider = ttk.Scale(distance_frame, from_=1, to=2*DEFAULT_MAX_DISTANCE,
                                   variable=self.distance_var, orient=tk.HORIZONTAL,
                                   command=self._on_distance_change)
        self.distance_slider.pack(fill=tk.X, padx=10, pady=5, expand=True)

        # Initial setup
        self._update_map_marker(initial_lat, initial_lon)
        self._update_event_markers() # Add event markers to map


    def _setup_map(self):
        """Setup the basic map appearance."""
        self.ax.set_xlim(MAP_LON_LIMITS)
        self.ax.set_ylim(MAP_LAT_LIMITS)

        map_width = MAP_LON_LIMITS[1] - MAP_LON_LIMITS[0]
        map_height = MAP_LAT_LIMITS[1] - MAP_LAT_LIMITS[0]
        aspect_ratio = map_width / map_height
        
        # Display the image as background
        map_path = os.path.join(ROOT_DIR, "assets/map.png")          
        map_img = mpimg.imread(map_path)
        self.ax.imshow(map_img, 
                      extent=[MAP_LON_LIMITS[0], MAP_LON_LIMITS[1], 
                              MAP_LAT_LIMITS[0], MAP_LAT_LIMITS[1]], 
                      aspect=aspect_ratio, 
                      zorder=0)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_title("Click to Set Location", fontsize=10)


    def _update_map_marker(self, lat, lon):
        """Update the user location marker and radius circle on the map."""
        # Remove previous marker and circle if they exist
        if self.user_marker:
            self.user_marker.remove()
            self.user_marker = None
        if self.radius_circle:
            self.radius_circle.remove()
            self.radius_circle = None

        # Add currenct location marker
        self.user_marker = self.ax.scatter(lon, lat, s=60, color='red', marker='o', zorder=5, label="Your Location")

        # Add radius circle
        radius_km = self.distance_var.get()
        
        # Convert radius from km to degrees
        # 111 km per degree of latitude 
        radius_lat_degrees = radius_km/111
        
        # Longitude degrees per kilometer varies with latitude
        # At the equator, 1 degree of longitude = 111 km
        # At latitude φ, 1 degree of longitude = 111 * cos(φ) km
        radius_lon_degrees = radius_km/(111 * np.cos(np.radians(lat)))
        
        # Create an ellipse with appropriate axes lengths
        self.radius_circle = Ellipse((lon, lat), 
                                    width=2*radius_lon_degrees, 
                                    height=2*radius_lat_degrees, 
                                    color='red', fill=False,
                                    alpha=0.5, linestyle='--', zorder=4, 
                                    label=f"{radius_km} km Radius")
        self.ax.add_patch(self.radius_circle)

        # Update the legend with user marker and radius circle
        handles = [self.user_marker, self.radius_circle]
        labels = ["Your Location", f"{radius_km} km Radius"]
        self.ax.legend(handles=handles, loc='upper right', fontsize=8)

        self.canvas.draw_idle()


    def _on_map_click(self, event):
        """Handle map click: update coords, marker, and notify app."""
        if event.inaxes == self.ax and event.xdata is not None and event.ydata is not None:
            lat = round(event.ydata, 4)
            lon = round(event.xdata, 4)

            self.lat_var.set(lat)
            self.lon_var.set(lon)
            self._update_map_marker(lat, lon)
            self._notify_app()


    def _update_location_from_inputs(self, event=None):
        """Update map marker from lat/lon entry fields and notify app."""
        try:
            lat = self.lat_var.get()
            lon = self.lon_var.get()
            # Basic validation
            if MAP_LAT_LIMITS[0] <= lat <= MAP_LAT_LIMITS[1] and \
               MAP_LON_LIMITS[0] <= lon <= MAP_LON_LIMITS[1]:
                self._update_map_marker(lat, lon)
                self._notify_app()
            else:
                print("Warning: Coordinates outside expected map bounds.")
        except tk.TclError:
            print("Error: Invalid latitude/longitude input.") # Handle non-numeric input


    def _on_distance_change(self, value_str):
        """Handle distance slider change: update label, marker, and notify app."""
        distance = int(float(value_str))
        self.distance_label.config(text=f"{distance} km")
        # Redraw radius circle
        self._update_map_marker(self.lat_var.get(), self.lon_var.get())
        self._notify_app()


    def _notify_app(self):
        """Inform the application coordinator about the preference change."""
        try:
             lat = self.lat_var.get()
             lon = self.lon_var.get()
             distance = self.distance_var.get()
             self.app.location_preference_updated(lat, lon, distance)
        except tk.TclError:
             print("Error notifying app due to invalid coordinate values.")


    def _update_event_markers(self):
        """Add event markers to the map."""
        # Clear any existing event markers
        for marker in self.event_markers:
            if marker:
                marker.remove()
        self.event_markers = []

        # Get events from the app coordinator
        events = self.app.service.events

        if not events:
            return

        # Add markers for each event
        for event in events:
            event_marker = self.ax.scatter(
                event.longitude, 
                event.latitude, 
                s=40, 
                color='blue', 
                marker='^', 
                alpha=0.7,
                zorder=3
            )
            # Add a small label with event name
            self.ax.annotate(
                event.name,
                (event.longitude, event.latitude),
                fontsize=8,
                ha='center',
                va='bottom',
                xytext=(0, 5),
                textcoords='offset points',
                alpha=0.8
            )
            self.event_markers.append(event_marker)

        self.canvas.draw_idle()


    def load_preferences(self):
        """Reload preferences from the service."""
        prefs = self.app.get_current_preferences()
        lat = prefs.location['latitude']
        lon = prefs.location['longitude']
        distance = prefs.max_distance
        self.lat_var.set(lat)
        self.lon_var.set(lon)
        self.distance_var.set(distance)
        self.distance_label.config(text=f"{distance} km")
        self._update_map_marker(lat, lon)
        self._update_event_markers()
