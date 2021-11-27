import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import mediapipe

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        #Configuring main window to stay at top-left corner and always on top of other windows

        #Making window not resizable
        self.window.resizable(False, False)

        #Stay always on top of other windows
        self.window.attributes('-topmost', True)

        #Remove toolbar so user cant move window
        self.window.overrideredirect(True)

        #Set backgroung color
        self.window.configure(background="#F5DD84")
        self.video_source = video_source

        #Buttons
        self.mouse_btn=tkinter.Button(window, bg="#6FC8EB" ,text="Mouse Control", width=12, height=4)
        self.mouse_btn.grid(row=0, column=0,pady=10)

        self.draw_btn=tkinter.Button(window, bg="#6FC8EB" , text="Draw", width=12, height=4)
        self.draw_btn.grid(row=0, column=1)

        self.type_btn=tkinter.Button(window, bg="#6FC8EB" , text="Type", width=12, height=4)
        self.type_btn.grid(row=0, column=2)

        self.cam_btn=tkinter.Button(window, bg="#6FC8EB" , text="Camera On/Off", width=12, height=4, command=self.cam_switch)
        self.cam_btn.grid(row=0, column=3)

        self.exit_btn=tkinter.Button(window, bg="#6FC8EB" , text="Exit", width=12, height=4, command=self.exit)
        self.exit_btn.grid(row=0, column=4)

        #Get frames from MyVideoCapture class and display them in a canvas widget
        self.vid = MyVideoCapture(self.video_source)
        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.grid(row=1, column = 0, columnspan = 5)

        self.delay = 10
        self.pTime = 0
        self.update()
        self.window.mainloop()

    #This method will be used to show/hide camera display
    def cam_switch(self):
        if (self.canvas.cget('state') == "normal"):
            self.window.geometry("644x90")
            self.canvas.config(state='disable')

        else:
            self.window.geometry("644x555")
            self.canvas.config(state='normal')

    #Since toolbar is removed a custom exit method is required
    def exit(self):
        self.window.destroy()
        self.window = None

    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            #Display fps
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            cv2.putText(frame, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)
            
            #Draw landmarks
            mpHands = mediapipe.solutions.hands
            hands = mpHands.Hands()
            mpDraw = mediapipe.solutions.drawing_utils
            results = hands.process(frame)
            if results.multi_hand_landmarks:
                for h in results.multi_hand_landmarks:
                    mpDraw.draw_landmarks(frame, h, mpHands.HAND_CONNECTIONS);
                    
            #Update frame
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
 
        self.window.after(self.delay, self.update)

class MyVideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
 
# Release the video source when the object is destroyed
def __del__(self):
    if self.vid.isOpened():
        self.vid.release()
        
# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")
