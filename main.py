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


class App:
    def __init__(self, window):
        ###---------- Main Window Configurations ----------###
        # Main window will stay at top-left corner and always on top of other windows
        self.window = window
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        self.window.configure(background="#FFE547")

        ###---------- Building UI ----------###
        # Buttons
        buttonLabel = tkinter.Label(self.window, borderwidth=4, relief="ridge")
        buttonLabel.configure(background="#FFE547")
        buttonLabel.grid(row = 0, column = 0, columnspan = 5)

        self.mouse_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Mouse Control", width=12, height=4, command=self.mouse_control)
        self.mouse_btn.grid(row=0, column=0, padx=(5,33),pady=10)
        self.m_is_on = False

        self.draw_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Draw", width=12, height=4, command=self.drawing)
        self.draw_btn.grid(row=0, column=1, padx=(0,33),pady=10)
        self.d_is_on = False

        self.type_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Type", width=12, height=4, command=self.typing)
        self.type_btn.grid(row=0, column=2, padx=(0,33),pady=10)
        self.t_is_on = False

        self.cam_btn=tkinter.Button(buttonLabel, bg="#50BBEB", text="Camera On/Off", width=12, height=4, command=self.canvas_toggle)
        self.cam_btn.grid(row=0, column=3, padx=(0,33),pady=10)

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
        self.start = 0 # Using for fps calcutalion
        self.display_switch = False
        user32 = ctypes.windll.user32
        self.width, self.height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.click = 0

        # Start update thread
        read_thread = Thread(target = self.update, args=(), daemon=True)
        read_thread.start()

        self.window.mainloop()

    ###---------- Buttons' Functions ----------###

    # This method will be used to show/hide camera display
    def canvas_toggle(self):
        if (self.canvas.cget('state') == "normal"):
            self.canvas.grid_remove()
            self.canvas.config(state='disable')
            self.cam_btn.config(bg="#6FC8EB")
            self.display_switch = False
        else:
            self.canvas.grid()
            self.canvas.config(state='normal')
            self.cam_btn.config(bg="#2B7DF0")
            self.display_switch = True

    def mouse_control(self):
        if self.m_is_on == False and self.d_is_on == False and self.t_is_on == False:
            self.m_is_on = True
            self.mouse_btn.config(bg="#2B7DF0")
        elif self.m_is_on == True and self.d_is_on == False and self.t_is_on == False:
            self.m_is_on = False
            self.mouse_btn.config(bg="#6FC8EB")
        else:
            messagebox.showerror("ERROR", "Disable other function!")

    def drawing(self):
        if self.m_is_on == False and self.d_is_on == False and self.t_is_on == False:
            self.d_is_on = True
            self.draw_btn.config(bg="#2B7DF0")
            self.side_window.deiconify()
        elif self.m_is_on == False and self.d_is_on == True and self.t_is_on == False:
            self.d_is_on = False
            self.draw_btn.config(bg="#6FC8EB")
            self.side_window.withdraw()
        else:
            messagebox.showerror("ERROR", "Disable other function!")

    def typing(self):
        if self.m_is_on == False and self.d_is_on == False and self.t_is_on == False:
            self.t_is_on = True
            self.type_btn.config(bg="#2B7DF0")
            self.side_window.deiconify()
        elif self.m_is_on == False and self.d_is_on == False and self.t_is_on == True:
            self.t_is_on = False
            self.type_btn.config(bg="#6FC8EB")
            self.side_window.withdraw()
        else:
            messagebox.showerror("ERROR", "Disable other function!")


    ###---------- UI Functions -----------###
    # Since toolbar is removed a custom exit method is required
    def exit(self):
        self.window.destroy()
        self.side_window.destroy()
        self.window, self.side_window = None, None

    # Update application
    def update(self):
        while True:
            ret, self.frame, results = self.vid.get_frame(self.display_switch)
            end = time.time()
            fps = 1 / (end - self.start)
            self.start = end
            #print("FPS:", int(fps))

            if ret:
                ###---------- Display ----------###
                if self.canvas.cget('state') == 'normal':
                    # Display fps
                    cv2.putText(self.frame, str(int(fps)),(20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)

                    # Send video frame to canvas
                    self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
                    self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

                ###---------- Create Landmark List ----------###
                if results.multi_hand_landmarks:
                    # Give result set and get landmark list from thread
                    markList = list()
                    lm_thread = Thread(target=self.get_landmarks, args=(results, markList), daemon=True)
                    lm_thread.start()
                    lm_thread.join()

                    self.thumb = markList[4]
                    self.index = markList[8]
                    self.middle = markList[12]
                    self.ring = markList[16]
                    self.pinky = markList[20]

                    ###---------- Mouse Control And Drawing ----------###
                    if self.m_is_on or self.d_is_on:
                        self.mouse()

                    ###---------- Typing ----------###
                    if self.t_is_on:
                        pass

    ###---------- Process Functions ----------###
    def get_landmarks(self, results, markList):
        tracker = ht.HandTracker(results)
        tracker.get_hand_coordinates(markList)
        # Check if thumb, index and middle finger tips are in frame
        if tracker.check_fingers(markList) == False:
            print("Your hand is out of view!")

    # Mouse control decisions    
    def mouse(self):
        idle = False
        # Left click if thumb and middle finger touched
        if self.distance(self.thumb, self.middle) < 30:
            self.click += 1
            if self.click % 10 == 0:
                pyautogui.click()

        # Right click if thumb and ring finger touched
        if self.distance(self.thumb, self.ring) < 30:
            self.click += 1
            if self.click % 10 == 0:
                pyautogui.click(button="right")

        # Stay idle if thumb and pinky finger touched 
        if self.distance(self.thumb, self.pinky) < 30:
            idle = True

        # Move mouse if not idle
        if idle == False:
            # Scale x, y coordinates to match screen size
            x = np.interp(self.index[1], (80, 560), (0, self.width))
            y = np.interp(self.index[2], (80, 400), (0, self.height))

            # Move cursor in a thread
            mouse_thread = Thread(target=self.move_cursor, args=(x, y, ), daemon=True)
            mouse_thread.start()
            

    # Get distance between two landmarks
    def distance(self, finger1, finger2):
        finger1_x, finger1_y = finger1[1:]
        finger2_x, finger2_y = finger2[1:]
        dist = math.sqrt((finger2_x - finger1_x)**2 + (finger2_y - finger1_y)**2)
        return int(dist)

    def move_cursor(self, x, y):
        pyautogui.moveTo(x,y)


app = App(tkinter.Tk())