import cv2
import mediapipe

# This object reads camera frames then apply mediapipe landmarks
# on frames and return that frame and medipipe results of frame
class VideoCapture:
    def __init__(self, video_source = 0):
        # Camera setup
        self.vid = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)

        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.vid.set(3, 640)
        self.vid.set(4, 480)

        # Initilialize hands module
        self.mpHands = mediapipe.solutions.hands
        self.hands = self.mpHands.Hands(False, 1, 1, 0.5, 0.5)
        self.mpDraw = mediapipe.solutions.drawing_utils

    def get_frame(self, display=False):
        if self.vid.isOpened():
            # Read frame and flip vertically for syncronize with movement direction
            ret, frame = self.vid.read()
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.rectangle(frame, (80, 80), (560, 400), (255, 0, 0), 1)

            results = self.hands.process(frame)
            # Apllying landmarks to frame
            if display==True:
                frame = self.display_lmarks(frame, results)

            if ret:
                return (ret, frame, results)
            else:
                return (ret, None)
        else:
            return (ret, None)

    def display_lmarks(self, frame, results):
        if results.multi_hand_landmarks:
            for h in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(frame, h, self.mpHands.HAND_CONNECTIONS);
        return frame

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()