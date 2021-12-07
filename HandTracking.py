import mediapipe

class HandTracker:
	def __init__(self, mode=False, maxHands = 2, detectionCon = 0.5, trackingCon = 0.5):
		self.mode = mode
		self.maxHands = maxHands
		self.detectionCon = detectionCon
		self.trackingCon = trackingCon

		self.mpHands = mediapipe.solutions.hands
		self.hands = self.mpHands.hands(self.mode,self.maxHands, self.detectionCon, self.trackingCon)

	def get_hand_coordinates(self, cap):
		markList = list()
		results = self.hands.process(cap)
		results = self.hands.multi_hand_landmarks
		if results.multi_hand_landmarks:
			for id, mark in enumarate(results.multi_hand_landmarks):
				x, y, c = cap.shape
				x_pix , y_pix = int(mark.x * w), int(mark.y * h)
				#tip of thumb, index and middle finger
				if id == 4 or id == 8 or id == 12:
					markList.append([id, x_pix, y_pix])
					
		return markList
