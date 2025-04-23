# main.py
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from gui.app import EventRecommenderApp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Event Recommendation System")
    root.geometry("1200x800")
    app = EventRecommenderApp(root)
    root.mainloop()