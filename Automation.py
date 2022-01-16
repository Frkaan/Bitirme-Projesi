#import autopy
import pyautogui
import math
import ctypes
import numpy as np

class Automator:
	def __init__(self, fingers, prevFingers):
		self.thumb = fingers[0]
		self.index = fingers[1]
		self.middle = fingers[2]

		self.pThumb = prevFingers[0]
		self.pIndex = prevFingers[1]
		self.pMiddle = prevFingers[2]


	# Get distance between two landmarks
	def distance(self, finger1, finger2):
		finger1_x, finger1_y = finger1[1:]
		finger2_x, finger2_y = finger2[1:]
		dist = math.sqrt((finger2_x - finger1_x)**2 + (finger2_y - finger1_y)**2)
		
		return int(dist)

	def mouse_control(self):
		click = False
		if self.distance(self.thumb, self.index) < 20:
			click = True
			#print("thumb-index:", self.distance(self.thumb, self.index))

		if self.distance(self.thumb, self.middle) < 20:
			click = True
			#print("thumb-middle:", self.distance(self.thumb, self.middle))

		if self.distance(self.index, self.middle) < 20:
			click = True
			#print("middle-index:", self.distance(self.index, self.middle))

		if click == False:
			print("move")


	def detect_mode(self):
		pass
		

class Automator2:
	def __init__(self, fingers):
		self.thumb = fingers[0]
		self.index = fingers[1]
		self.middle = fingers[2]

		user32 = ctypes.windll.user32
		self.height, self.width = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

	# Get distance between two landmarks
	def distance(self, finger1, finger2):
		finger1_x, finger1_y = finger1[1:]
		finger2_x, finger2_y = finger2[1:]
		dist = math.sqrt((finger2_x - finger1_x)**2 + (finger2_y - finger1_y)**2)
		#print(dist)
		return int(dist)

	def mouse_control(self):
		click = False
		if self.distance(self.thumb, self.index) < 20:
			click = True
			#print("thumb-index:", self.distance(self.thumb, self.index))

		if self.distance(self.thumb, self.middle) < 20:
			click = True
			#print("thumb-middle:", self.distance(self.thumb, self.middle))

		if self.distance(self.index, self.middle) < 20:
			click = True
			#print("middle-index:", self.distance(self.index, self.middle))

		if click == False:
			#print("move")
			x = self.index[1] * (self.width/640)#np.interp(self.index[1], (0, 640), (0, self.width))
			y = self.index[2] * (self.height/480)#np.interp(self.index[2], (0, 480), (0, self.height))
			pyautogui.moveTo(x,y)