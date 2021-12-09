import mediapipe

# This object creates a hand module copy 
# with a list that holds landmarks' coordinates
class HandTracker:
	def __init__(self, mode=False, maxHands = 2, modelComplexity = 1, detectionCon = 0.5, trackingCon = 0.5):
		self.mode = mode
		self.maxHands = maxHands
		self.modelComplex = modelComplexity
		self.detectionCon = detectionCon
		self.trackingCon = trackingCon

		self.mpHands = mediapipe.solutions.hands
		self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionCon, self.trackingCon)

	def get_hand_coordinates(self, frame):
		markList = list()

		results = self.hands.process(frame)
		if results.multi_hand_landmarks:
			hand = results.multi_hand_landmarks[0]
			for id, mark in enumerate(hand.landmark):
				height, width, channel = frame.shape
				x_pix , y_pix = int(mark.x * width), int(mark.y * height)
				markList.append([id, x_pix, y_pix])

		return markList
