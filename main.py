import tkinter
from tkinter import messagebox
import cv2
import time
import ctypes
import math
import pyautogui
import numpy as np
import PIL.Image, PIL.ImageTk
from threading import Thread

import SideWindow as sw
import HandTracking as ht
import VideoCapture as vp

lastClickX = 0
lastClickY = 0

class App:
    def __init__(self, window):
        ###---------- Main Window Configurations ----------###
        # Main window will stay at top-left corner and always on top of other windows
        self.window = window
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        self.window.bind('<Button-1>', self.SaveLastClickPos)
        self.window.bind('<B1-Motion>', self.Dragging)
        self.window.configure(background="#FFE547")

        ###---------- Building UI ----------###
        # Buttons Label
        buttonLabel = tkinter.Label(self.window, borderwidth=4, relief="ridge")
        buttonLabel.configure(background="#FFE547")
        buttonLabel.grid(row = 0, column = 0, columnspan = 5)
        # Button 1 - Mouse Control
        self.mouse_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Mouse Control", width=12, height=4, command=self.mouse_control)
        self.mouse_btn.grid(row=0, column=0, padx=(5,33),pady=10)
        self.m_is_on = False
        # Button 2 - Type
        self.type_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Type Control", width=12, height=4, command=self.typing)
        self.type_btn.grid(row=0, column=1, padx=(0,33),pady=10)
        self.t_is_on = False
        # Button 3 - Camera On/Off
        self.cam_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Camera On/Off", width=12, height=4, command=self.canvas_toggle)
        self.cam_btn.grid(row=0, column=2, padx=(0,33),pady=10)
        # Button 4 - Open Palette
        self.palette_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Palette On/Off", width=12, height=4, command=self.palette_toggle)
        self.palette_btn.grid(row=0, column=3, padx=(0,33),pady=10)
        self.p_is_on = False
        # Button 5 - Exit
        self.exit_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Exit", width=12, height=4, command=self.exit)
        self.exit_btn.grid(row=0, column=4, padx=(0,33),pady=10)

        # Canvas for video display
        self.canvas = tkinter.Canvas(self.window, width = 640, height = 480)
        self.canvas.grid(row = 1, column = 0, columnspan = 5)
        self.canvas.config(state='disable')
        self.canvas.grid_remove()

        #Side window for draw and type functions, hidden at start
        self.side_window = sw.SideWindow()
        self.side_window.withdraw()

        ###----------- Video Capture -----------###
        self.vid = vp.VideoCapture()

        # Get screen size for mouse control
        user32 = ctypes.windll.user32
        self.width, self.height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        self.click = 0 # Delay variable for click event
        self.start = 0 # Fps calculation start time
        self.tracker = ht.HandTracker() # Init hand tracking module
        
        # Start update thread
        read_process_thread = Thread(target = self.update, args=(), daemon=True)
        read_process_thread.start()

        self.window.mainloop()

    def SaveLastClickPos(self, event):
        global lastClickX, lastClickY
        lastClickX = event.x
        lastClickY = event.y


    def Dragging(self, event):
        x, y = event.x - lastClickX + self.window.winfo_x(), event.y - lastClickY + self.window.winfo_y()
        self.window.geometry("+%s+%s" % (x , y))

    ###---------- Buttons' Functions ----------###
    # Mouse control button's function
    def mouse_control(self):
        if self.m_is_on == False  and self.t_is_on == False:
            self.m_is_on = True
            self.mouse_btn.config(bg="#2B7DF0")
        elif self.m_is_on == True and self.t_is_on == False:
            self.m_is_on = False
            self.mouse_btn.config(bg="#6FC8EB")
        else:
            messagebox.showerror("ERROR", "Disable Type Function!")

    # Type button's function
    def typing(self):
        if self.m_is_on == False and self.t_is_on == False:
            self.t_is_on = True
            self.type_btn.config(bg="#2B7DF0")
        elif self.m_is_on == False and self.t_is_on == True:
            self.t_is_on = False
            self.type_btn.config(bg="#6FC8EB")
        else:
            messagebox.showerror("ERROR", "Disable Mouse Control Function!")

    # Draw button's function
    def palette_toggle(self):
        if self.p_is_on == False:
            self.palette_btn.config(bg="#2B7DF0")
            self.p_is_on = True
            self.side_window.deiconify()
        else:
            self.palette_btn.config(bg="#6FC8EB")
            self.p_is_on = False
            self.side_window.withdraw()



    # Camera On/Off button's function
    def canvas_toggle(self):
        if (self.canvas.cget('state') == "normal"):
            self.canvas.grid_remove()
            self.canvas.config(state='disable')
            self.cam_btn.config(bg="#6FC8EB")
        else:
            self.canvas.grid()
            self.canvas.config(state='normal')
            self.cam_btn.config(bg="#2B7DF0")


    ###---------- UI Functions -----------###
    # Since toolbar is removed a custom exit method is required
    def exit(self):
        self.window.destroy()
        self.side_window.destroy()
        self.window, self.side_window = None, None

    # Update application
    def update(self):
        while True:
            # Read frame, return flag, frame and landmark results
            # If you want to see landmarks use True instead
            ret, self.frame, self.results = self.vid.get_frame(True)
            # Calculate fps
            end = time.time()
            self.fps = 1 / (end - self.start)
            self.start = end
            #print("FPS:", int(fps))

            # Check if frame captured successfully
            if ret:
                # When canvas is on, display frames
                if self.canvas.cget('state') == 'normal':
                    self.display()
                # If hand is detected do processing
                if self.results.multi_hand_landmarks:
                    self.process()

                    ###---------- Mouse Control And Drawing ----------###
                    if self.m_is_on:
                        self.mouse()

                    ###---------- Typing ----------###
                    if self.t_is_on:
                        pass

    ###---------- Display Video ----------###
    def display(self):
        # Display fps
        cv2.putText(self.frame, str(int(self.fps)),(20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)

        # Send video frame to canvas
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
        self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

    ###---------- Get Finger Landmarks ----------###
    def process(self):
        self.tracker.load_results(self.results)
        markList = self.tracker.get_hand_coordinates()
        # We only need tip of the fingers
        self.thumb = markList[4]
        self.index = markList[8]
        self.middle = markList[12]
        self.ring = markList[16]
        self.pinky = markList[20]

        if self.tracker.check_fingers(markList) == False:
            print("Your hand is out of view!")

    # Mouse control decisions    
    def mouse(self):
        hold = False
        if self.click >100:
            self.click -= 100
        # Left click if thumb and middle finger touched
        if self.distance(self.thumb, self.middle) < 25:
            self.click += 1
            if self.click % 10 == 0:
                pyautogui.click()

        # Right click if thumb and ring finger touched
        if self.distance(self.thumb, self.ring) < 20:
            self.click += 1
            if self.click % 10 == 0:
                pyautogui.click(button="right")

        # Enable hold mode if thumb and pinky finger are together 
        if self.distance(self.thumb, self.pinky) < 20:
            hold = True

        # Scale x, y coordinates to match screen size
        x = np.interp(self.index[1], (80, 560), (0, self.width))
        y = np.interp(self.index[2], (80, 400), (0, self.height))

        
        x_now, y_now = pyautogui.position()
        length = math.sqrt(pow(abs(x - x_now),2) + pow(abs(y - y_now),2))

        if(length>5):
            # Move cursor in a thread
            mouse_thread = Thread(target=self.move_cursor, args=(x, y, hold), daemon=True)
            mouse_thread.start()
            

    # Get distance between two landmarks
    def distance(self, finger1, finger2):
        finger1_x, finger1_y = finger1[1:]
        finger2_x, finger2_y = finger2[1:]
        dist = math.sqrt((finger2_x - finger1_x)**2 + (finger2_y - finger1_y)**2)
        return int(dist)

    def move_cursor(self, x, y, hold):
        if hold == True: 
            pyautogui.dragTo(x,y, button="left")
        else: 
            pyautogui.moveTo(x, y) 
        

app = App(tkinter.Tk())
