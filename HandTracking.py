import mediapipe

# This object creates a list from medipipe result set
# List holds landmarks' coordinates
class HandTracker:
	def __init__(self, results):
		self.results = results

	def get_hand_coordinates(self, markList):
		if self.results.multi_hand_landmarks:
			hand = self.results.multi_hand_landmarks[0]
			for id, mark in enumerate(hand.landmark):
				x_pix , y_pix = int(mark.x * 640), int(mark.y * 480)
				markList.append([id, x_pix, y_pix])

		return markList
