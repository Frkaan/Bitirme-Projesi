import tkinter
import cv2
import time
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
        self.window.configure(background="#F5DD84")

        ###---------- Building UI ----------###
        # Buttons
        buttonLabel = tkinter.Label(self.window, borderwidth=4, relief="ridge")
        buttonLabel.configure(background="#F5DD84")
        buttonLabel.grid(row = 0, column = 0, columnspan = 5)

        self.mouse_btn=tkinter.Button(buttonLabel, bg="#6FC8EB", text="Mouse Control", width=12, height=4, command=self.mouse_control)
        self.mouse_btn.grid(row=0, column=0, padx=(5,33),pady=10)
        self.m_is_on = False

        self.draw_btn=tkinter.Button(buttonLabel, bg="#6FC8EB", text="Draw", width=12, height=4, command=self.drawing)
        self.draw_btn.grid(row=0, column=1, padx=(0,33),pady=10)
        self.d_is_on = False

        self.type_btn=tkinter.Button(buttonLabel, bg="#6FC8EB", text="Type", width=12, height=4, command=self.typing)
        self.type_btn.grid(row=0, column=2, padx=(0,33),pady=10)
        self.t_is_on = False

        self.cam_btn=tkinter.Button(buttonLabel, bg="#6FC8EB", text="Camera On/Off", width=12, height=4, command=self.canvas_toggle)
        self.cam_btn.grid(row=0, column=3, padx=(0,33),pady=10)

        self.exit_btn=tkinter.Button(buttonLabel, bg="#6FC8EB", text="Exit", width=12, height=4, command=self.exit)
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

        # Start update thread
        read_thread = Thread(target = self.update, args=(), daemon=True)
        read_thread.start()

        self.window.mainloop()

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
            print("Starting mouse control...")
            self.m_is_on = True
            self.mouse_btn.config(bg="#2B7DF0")
        elif self.m_is_on == True and self.d_is_on == False and self.t_is_on == False:
            print("Stopping mouse control...")
            self.m_is_on = False
            self.mouse_btn.config(bg="#6FC8EB")
        else:
            print("Disable other functions!")

    def drawing(self):
        if self.m_is_on == False and self.d_is_on == False and self.t_is_on == False:
            print("Starting drawing...")
            self.d_is_on = True
            self.draw_btn.config(bg="#2B7DF0")
            self.side_window.deiconify()
        elif self.m_is_on == False and self.d_is_on == True and self.t_is_on == False:
            print("Stopping drawing...")
            self.d_is_on = False
            self.draw_btn.config(bg="#6FC8EB")
            self.side_window.withdraw()
        else:
            print("Disable other functions!")

    def typing(self):
        if self.m_is_on == False and self.d_is_on == False and self.t_is_on == False:
            print("Starting typing...")
            self.t_is_on = True
            self.type_btn.config(bg="#2B7DF0")
            self.side_window.deiconify()
        elif self.m_is_on == False and self.d_is_on == False and self.t_is_on == True:
            print("Stopping typing...")
            self.t_is_on = False
            self.type_btn.config(bg="#6FC8EB")
            self.side_window.withdraw()
        else:
            print("Disable other functions!")

    # Since toolbar is removed a custom exit method is required
    def exit(self):
        self.window.destroy()
        self.side_window.destroy()
        self.window, self.side_window = None, None

    # Update application
    def update(self):
        while True:
            ret, frame, results = self.vid.get_frame(self.display_switch)
            end = time.time()
            fps = 1 / (end - self.start)
            self.start = end
            print("FPS:", int(fps))

            if ret:
                ###---------- Display ----------###
                if self.canvas.cget('state') == 'normal':
                    # Display fps
                    cv2.putText(frame, str(int(fps)),(20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)

                    # Send video frame to canvas
                    self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                    self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

                ###---------- Create Landmark List ----------###
                markList = list()
                lm_thread = Thread(target=self.get_landmarks, args=(results, markList), daemon=True)
                lm_thread.start()
                lm_thread.join()

                if len(markList)!= 0:
                    print(markList)
                    pass

                ###---------- Mouse Control ----------###
                if self.m_is_on:
                    pass

                ###---------- Drawing ----------###
                if self.d_is_on:
                    pass

                ###---------- Typing ----------###
                if self.t_is_on:
                    pass

            # Use sleep to be able to catch all frames, but FPS drops
            # When not used FPS gets higher and ui lose some frames
            # but it is not important because processing creates a delay
            # that work likes a sleep
            #time.sleep(0.03)

        #self.window.after(33, self.update)

    def get_landmarks(self, results, markList):
        tracker = ht.HandTracker(results)
        lmList = tracker.get_hand_coordinates(markList)
        return lmList

    def mouse(self):
        pass

    def draw(self):
        pass

    def type(self):
        pass


app = App(tkinter.Tk())