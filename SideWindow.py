import tkinter
from tkinter import ttk

# This side window will be used for draw and type functions
class SideWindow:
    def __init__(self):
        ###---------- Side Window Configurations ----------###
        self.side_window = tkinter.Tk()
        self.side_window.resizable(False, False)
        self.side_window.attributes('-topmost', True)
        self.side_window.attributes('-alpha', 0.5)
        self.side_window.overrideredirect(True)
        self.side_window.configure(background="#FFFFFF")
        self.side_window.grid_columnconfigure(0, weight=1)
        self.screen_width = self.side_window.winfo_screenwidth()
        self.screen_height = self.side_window.winfo_screenheight()
        self.side_window.geometry("%dx%d+%d+%d" % (self.screen_width-650, self.screen_height, 644, 0))

        ###---------- Building UI ----------###
        # Top Bar
        self.top_bar = tkinter.Label(self.side_window, bg = "#F5DD84", borderwidth=4, relief="ridge")
        self.top_bar.grid(sticky="ew")

        # Top Bar Labels
        self.label = tkinter.Label(self.top_bar, text = "Opacity", bg = "#6FC8EB", borderwidth=2, relief="ridge")
        self.label.config(font=("Courier Bold", 20))
        self.label.grid(row = 1, column=0, padx=20, pady=10)

        # Widgets
        self.slider = ttk.Scale(self.top_bar,from_ = 0.2, to = 1.0, value = 1.0, orient = tkinter.HORIZONTAL,command=self.slide)
        self.slider.grid(row = 2, column=0, padx=20, pady = 4)

    # A slider is used for changing the opacity of side window
    def slide(self, x):
        self.side_window.attributes('-alpha', self.slider.get())


    # These method makes object behave like tkinter window
    def withdraw(self):
        self.side_window.withdraw()

    def deiconify(self):
        self.side_window.deiconify()

    def destroy(self):
        self.side_window.destroy()