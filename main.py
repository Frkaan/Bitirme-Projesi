import tkinter
from tkinter import messagebox
import cv2
import time
import ctypes
import string
import math
import pyautogui
pyautogui.FAILSAFE = False
import PIL.Image, PIL.ImageTk
from threading import Thread
import numpy as np
from keras.models import load_model
import SideWindow as sw
import HandTracking as ht
import VideoCapture as vp

LAST_CLICK_X = 0
LAST_CLICK_Y = 0
SHOW_LANDMARKS = False
IMAGE_DIM = 28

class App:
    def __init__(self, window):
        ###---------- Main Window Configurations ----------###
        # Main window will stay at top-left corner and always on top of other windows   
        self.window = window
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        self.window.configure(background="#FFE547")
        self.window.bind('<Button-1>', self.saveLastClickPos)
        self.window.bind('<B1-Motion>', self.dragging)
        
        ###---------- UI Elements ----------###
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

        # Side window for draw and type functions, hidden at start
        self.side_window = sw.SideWindow()
        self.side_window.withdraw()

        # Get screen size
        user32 = ctypes.windll.user32
        self.width, self.height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        ###----------- Video Capture -----------###
        self.vid = vp.VideoCapture()        

        self.click = 0 # Delay variable for click event
        self.start = 0 # Fps calculation start time
        self.hold = False # Mouse button hold variable
        self.tracker = ht.HandTracker() # Init hand tracking module

        self.capture_delay = 0 # Delay variable for handsign recognition

        # Load machine learning model
        self.predictor = load_model("ai_model")
        # Define pre-used prediction labels
        self.labels = [char for char in string.ascii_uppercase if char != "J" if char != "Z"]

        # Start update thread
        read_process_thread = Thread(target = self.update, args=(), daemon=True)
        read_process_thread.start()

        self.window.mainloop()

    # Make main window draggable
    def saveLastClickPos(self, event):
        global LAST_CLICK_X, LAST_CLICK_Y
        LAST_CLICK_X = event.x
        LAST_CLICK_Y = event.y

    def dragging(self, event):
        x, y = event.x - LAST_CLICK_X + self.window.winfo_x(), event.y - LAST_CLICK_Y + self.window.winfo_y()
        self.window.geometry("+%s+%s" % (x , y))

    ###---------- Buttons' Functions ----------###
    # Mouse control button's function
    def mouse_control(self):
        if self.m_is_on == False:
            if self.t_is_on == True:
                self.t_is_on = False
                self.type_btn.config(bg="#6FC8EB")
            self.m_is_on = True
            self.mouse_btn.config(bg="#2B7DF0")

        elif self.m_is_on == True and self.t_is_on == False:
            self.m_is_on = False
            self.mouse_btn.config(bg="#6FC8EB")

        else:
            messagebox.showerror("ERROR", "Please restart program!")

    # Type button's function
    def typing(self):
        if self.t_is_on == False:
            if self.m_is_on == True: 
                self.m_is_on = False
                self.mouse_btn.config(bg="#6FC8EB")
            self.t_is_on = True
            self.type_btn.config(bg="#2B7DF0")

        elif self.t_is_on == True and self.m_is_on == False:
            self.t_is_on = False
            self.type_btn.config(bg="#6FC8EB")
        
        else:
            messagebox.showerror("ERROR", "Please restart program!")

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
            ret, self.frame, self.results = self.vid.get_frame(SHOW_LANDMARKS)
            # Calculate fps
            end = time.time()
            self.fps = 1 / (end - self.start)
            self.start = end

            # Check if frame captured successfully
            if ret:
                # When canvas is on, display frames
                if self.canvas.cget('state') == 'normal':
                    self.display()
                # If hand is detected do processing
                if self.results.multi_hand_landmarks:
                    self.process()
                    ###---------- Mouse Control And Drawing ----------###
                    if self.m_is_on and not self.t_is_on:
                        self.mouse()

                    ###---------- Typing ----------###
                    if self.t_is_on and not self.m_is_on:
                        self.type_letter()

    ###---------- Display Video ----------###
    def display(self):
        # Display fps
        cv2.putText(self.frame, 'fps:'+str(int(self.fps)),(10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
        # Highlighting the borders of control fields
        # For mouse control
        if self.m_is_on and not self.t_is_on:
            cv2.putText(self.frame, 'KEEP YOUR HAND IN FRAME', (80, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.rectangle(self.frame, (80, 80), (560, 400), (255, 0, 0), 2)
        # For type control
        if self.t_is_on and not self.m_is_on:
            cv2.putText(self.frame, 'SHOW HANDSIGN HERE', (350, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.putText(self.frame, 'AND WAIT FOR RECOGNITION', (330, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.rectangle(self.frame, (320, 0), (640, 480), (255, 0, 0), 2)
            cv2.rectangle(self.frame, (320, 80), (640, 400), (255, 0, 0), 2)    

        # Send video frame to canvas
        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.frame))
        self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

    ###---------- Get Finger Landmarks ----------###
    def process(self):
        self.tracker.load_results(self.results)
        self.markList = self.tracker.get_hand_coordinates()
        # We only need tip of the fingers
        self.thumb = self.markList[4]
        self.index = self.markList[8]
        self.middle = self.markList[12]
        self.ring = self.markList[16]
        self.pinky = self.markList[20]

        if self.tracker.check_fingers(self.markList, [0, 0, 640, 480]) == False:
            print("Your hand is out of view!")

    # Mouse control decisions
    def mouse(self):
        if self.click > 100:
            self.click -= 100
        # Left click if thumb and middle finger touched
        if self.distance(self.thumb, self.middle) < 25:
            self.click += 1
            if self.click % 10 == 0:
                pyautogui.click()

        # Right click if thumb and ring finger touched
        if self.distance(self.thumb, self.ring) < 25:
            self.click += 1
            if self.click % 10 == 0:
                pyautogui.click(button="right")

        # Enable hold mode if thumb and pinky finger are together 
        if self.distance(self.thumb, self.pinky) < 25:
            self.click += 1
            if self.click % 10 == 0:
                if self.hold == False: 
                    pyautogui.mouseDown()
                    self.hold = True
                else: 
                    pyautogui.mouseUp()
                    self.hold = False

        # Scale x, y coordinates to match screen size
        x = np.interp(self.index[1], (80, 560), (0, self.width))
        y = np.interp(self.index[2], (80, 400), (0, self.height))

        # Calculate move amount for cursor
        x_now, y_now = pyautogui.position()
        length = math.sqrt(pow(abs(x - x_now),2) + pow(abs(y - y_now),2))

        if(length>5):
            # Move cursor in a thread
            mouse_thread = Thread(target=self.move_cursor, args=(x, y), daemon=True)
            mouse_thread.start()
            
    # Get distance between two landmarks
    def distance(self, finger1, finger2):
        finger1_x, finger1_y = finger1[1:]
        finger2_x, finger2_y = finger2[1:]
        dist = math.sqrt((finger2_x - finger1_x)**2 + (finger2_y - finger1_y)**2)
        return int(dist)

    # Cursor move method to be called in another thread
    def move_cursor(self, x, y):
        pyautogui.moveTo(x, y)

    # Detect, process, predict and type the handsign
    def type_letter(self):
        if self.tracker.check_fingers(self.markList, [320, 80, 640, 400]) == True:
            self.capture_delay += 1
            # Set a delay to give user enough time to position his handsign in showed area
            if self.capture_delay == 10:
                # Get one frame from detected handsign and process frame for prediction
                handsign = self.frame[80:400, 320:640] # crop frame
                #cv2.imwrite('img_raw.jpg', handsign)

                img = cv2.cvtColor(handsign, cv2.COLOR_BGR2GRAY)
                # For threshold #
                #blur = cv2.GaussianBlur(gray,(3,3),2)
                #adp_th = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
                #ret, img = cv2.threshold(adp_th, 0, 255, cv2.THRESH_OTSU)
                out = cv2.resize(img, (128,128), interpolation = cv2.INTER_AREA)
                out = out.reshape(1, 128, 128, 1) # reshape to model input

                # Make the prediction
                predicted_letter = self.make_pred(self.predictor, out)
                # Return to input area
                pyautogui.hotkey('alt', 'tab')
                # Type letter
                pyautogui.press(predicted_letter.lower())

                # Reset delay
                self.capture_delay = 0

                # Disable typing and enable mouse control
                self.type_btn.invoke()
                self.mouse_btn.invoke()

        # If hand is out of box restart delay counter
        else:
            self.capture_delay = 0
        
    # Make prediction using pretrained model
    def make_pred(self, predictor, img):
        pred = predictor.predict(img)
        pred_label = self.labels[np.argmax(pred)]
        return pred_label

if __name__ == "__main__":
    app = App(tkinter.Tk())