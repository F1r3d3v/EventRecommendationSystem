import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from gui.app import EventRecommenderApp

def app_quit():
    root.quit()
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", app_quit)
    root.title("Event Recommendation System")
    root.geometry("800x800")
    app = EventRecommenderApp(root)
    root.mainloop()
