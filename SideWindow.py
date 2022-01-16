import tkinter
from tkinter import ttk
from threading import Thread



lastx, lasty = None, None

# This side window will be used for draw and type functions
class SideWindow:
    def __init__(self):
        ###---------- Side Window Configurations ----------###
        self.side_window = tkinter.Tk()
        self.side_window.resizable(False, False)
        self.side_window.attributes('-topmost', True)
        self.side_window.attributes('-alpha', 1.0)
        self.side_window.overrideredirect(True)
        self.side_window.configure(background="#FFFFFF")
        self.side_window.grid_columnconfigure(0, weight=1)
        self.side_window.grid_rowconfigure(1, weight=1)
        self.screen_width = self.side_window.winfo_screenwidth()
        self.screen_height = self.side_window.winfo_screenheight()
        self.side_window.geometry("%dx%d+%d+%d" % (self.screen_width-650, self.screen_height, 644, 0))

        ###---------- Building UI ----------###
        # Top Bar
        self.top_bar = tkinter.Label(self.side_window, bg = "#FFE547", borderwidth=4, relief="ridge")
        self.top_bar.grid_columnconfigure(5,weight=1)
        self.top_bar.grid_rowconfigure(0,weight=1)
        self.top_bar.grid(row = 0, rowspan = 1, column = 0, columnspan = 5, sticky = "ew")

        # Opacity Setting
        self.opacity = tkinter.Label(self.top_bar, text = "Opacity", bg = "#50BBEB", borderwidth=2, relief="ridge")
        self.opacity.config(font=("Courier Bold", 20))
        self.opacity.grid(row = 0, column = 0, padx = 20, pady = 10)

        self.slider = ttk.Scale(self.top_bar, from_ = 0.2, to = 1.0, value = 1.0, orient = tkinter.HORIZONTAL,command=self.slide)
        self.slider.grid(row = 1, column = 0, padx = 20, pady = 4)

        # Brush & Eraser Size Setting
        self.size = tkinter.Label(self.top_bar, text = "Brush Size", bg = "#50BBEB", borderwidth=2, relief="ridge")
        self.size.config(font=("Courier Bold", 20))
        self.size.grid(row = 0, column = 1, padx = 20, pady = 10)

        self.size_slider = ttk.Scale(self.top_bar,from_ = 1, to = 10, value = 1, orient = tkinter.HORIZONTAL,command=self.slide)
        self.size_slider.grid(row = 1, column = 1, padx = 20, pady = 4)

        # Clear
        self.clear = tkinter.Button(self.top_bar, text= "Clear", bg= "#50BBEB", relief="ridge", command = self.clear_palette)
        self.clear.config(font=("Courier Bold", 20))
        self.clear.grid(row = 0, column = 2, padx = 20, pady = 10)

        # Selected Brush Color
        self.brush = tkinter.Label(self.top_bar, bg = "#000000", borderwidth=2, relief="ridge")
        self.brush.grid(row = 1, column = 2, padx = 20, pady = 4, sticky = "nsew")

        # Colors
        self.colors = tkinter.Label(self.top_bar, bg = "#ffffff", borderwidth=2, relief="ridge")
        self.colors.grid(row = 0, rowspan = 2, column = 3, columnspan = 3, padx = 20, pady = 5, sticky = "nsew")
        self.colors.grid_rowconfigure(0, weight=1)
        self.colors.grid_columnconfigure([0,1,2,3,4,5], weight=1)
        
        self.color_list = ["#000000", "#FF0000", "#0000FF", "#FFFF00", "#00FF00", "#FFFFFF"]
        self.color = "#000000"

        # Color Buttons
        self.black = tkinter.Button(self.colors, bg= self.color_list[0], bd=2, relief="ridge",command = lambda col = self.color_list[0]: self.select_color(col))
        self.black.grid(row=0, rowspan=2, column=0, sticky = "nsew")
        self.red = tkinter.Button(self.colors, bg= self.color_list[1], bd=2, relief="ridge",command = lambda col = self.color_list[1]: self.select_color(col))
        self.red.grid(row=0, rowspan=2, column=1, sticky = "nsew")
        self.blue = tkinter.Button(self.colors, bg= self.color_list[2], bd=2, relief="ridge",command = lambda col = self.color_list[2]: self.select_color(col))
        self.blue.grid(row=0, rowspan=2, column=2, sticky = "nsew")
        self.yellow = tkinter.Button(self.colors, bg= self.color_list[3], bd=2, relief="ridge",command = lambda col = self.color_list[3]: self.select_color(col))
        self.yellow.grid(row=0, rowspan=2, column=3, sticky = "nsew")
        self.green = tkinter.Button(self.colors, bg= self.color_list[4], bd=2, relief="ridge",command = lambda col = self.color_list[4]: self.select_color(col))
        self.green.grid(row=0, rowspan=2, column=4, sticky = "nsew")
        self.white = tkinter.Button(self.colors, bg= self.color_list[5], bd=2, text = "Eraser", relief="ridge",command = lambda col = self.color_list[5]: self.select_color(col))
        self.white.grid(row=0, rowspan=2, column=5, sticky = "nsew")

        # Palette
        self.palette = tkinter.Canvas(self.side_window, bg = "white", borderwidth = 6, relief = "ridge")
        self.palette.grid(row = 1,column = 0,sticky="nsew")
        self.palette.bind('<1>', self.activate_paint)

    # A slider is used for changing the opacity of side window
    def slide(self, x):
        self.side_window.attributes('-alpha', self.slider.get())

    # Copying tkinter window object functions
    def withdraw(self):
        self.side_window.withdraw()

    def deiconify(self):
        self.side_window.deiconify()

    def destroy(self):
        self.side_window.destroy()

    # Palette clearing method
    def clear_palette(self):
        self.palette.delete("all")

    # Select brush color
    def select_color(self, color):
        self.brush.config(bg=color)
        self.color = color

    # Drawing methods
    def activate_paint(self, e):
        global lastx, lasty
        self.palette.bind('<B1-Motion>', self.paint)
        lastx, lasty = e.x, e.y

    def paint(self, e):
        global lastx, lasty
        x, y = e.x, e.y
        self.palette.create_line((lastx, lasty, x, y), width=self.size_slider.get(), fill = self.color)
        lastx, lasty = x, y
