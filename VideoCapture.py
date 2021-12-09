import cv2
import mediapipe

class VideoCapture:
    def __init__(self, video_source = 0):
        self.vid = cv2.VideoCapture(video_source, cv2.CAP_DSHOW)

        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.vid.set(3, 640)
        self.vid.set(4, 480)

        # Initilialize hands module
        self.mpHands = mediapipe.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mediapipe.solutions.drawing_utils

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Open comment below to display landmarks on video feed
            frame = self.display_lmarks(frame)
            if ret:
                return (ret, frame)
            else:
                return (ret, None)
        else:
            return (ret, None)

    def display_lmarks(self, frame):
        results = self.hands.process(frame)
        if results.multi_hand_landmarks:
            for h in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(frame, h, self.mpHands.HAND_CONNECTIONS);
        return frame

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()