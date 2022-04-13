# Bitirme-Projesi

<!-- ABOUT THE PROJECT -->
## About The Project

In this project, an application will allow users to control mouse cursor and keyboard inputs on the computer by detecting the hand movements of the user. 

#### Application is divided into three parts.

- Controlling the mouse cursor on the computer as a result of moving the hand by showing it to the camera.
- Drawing on the screen by controlling the cursor with the hand movement.
- Writing with hand alphabet signs.

These sections will be briefly referred to as mouse control, drawing and typing functions. Thanks to these functions to be accessed from the application's interface, it will be possible to control the computer using without any peripherals.

### Built With
* [Python](https://python.org/)
* [OpenCV](https://opencv.org/)
* [MediaPipe](https://mediapipe.dev/)
* [Tensorflow](https://www.tensorflow.org/)
* [Keras](https://keras.io/getting_started/)

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
* Tkinter
  ```sh
  pip install tk
  ```
* PIL
  ```sh
  pip install pillow
  ```
* OpenCV
  ```sh
  pip install opencv-python
  ```
* PyAutoGui
  ```sh
  pip install pyautogui
  ```
* MediaPipe
  ```sh
  pip install mediapipe
  ```
* Tensorflow
  ```sh
  pip install tensorflow
  ```
* Keras
  ```sh
  pip install keras
  ```

### Installation
1. Clone the repo.
   ```sh
   git clone https://github.com/Frkaan/Final-Project.git
   ```
2. Install required packages.
3. Make sure you have a camera connected to computer and available.
4. Run code.

### How Code Works?
## Mouse Control Function
Program gets realtime video feed with OpenCV methods. Then applies Mediapipe hand module on hand and gets landmarks of hand. These landmarks returns with coordinates of where they exist on the video frame. Use these coordinates and scale them to our screen size and detect where it matches on computer screen. Lastly using PyAutoGui mouse move method move mouse cursor to determined coordinates.

* Move Mouse - Coordinates will be determined by tip of your index finger
* Left Click - Tap thumb with middle finger
* Right Click - Tap thumb with middle finger
* Hold Left Click - Tap and hold thumb with little finger

## Drawing Function
Main purpose of this function is to be able to draw and paint on screen during presentations for better impressions. Program has a basic canvas painting window for this objective. But what makes it unique for this project is, it has an opacity setting which makes canvas nearly invisible during drawing or painting on it. User can use Hold Left Click motion to draw on this canvas.

## Type Function
For this function program will be using an artificial intelligence model to classify the letter to type and this model will be working on ASL sign language hand signs. Creating and training the model is secondary goal of this project. After completing this goal, model will be integrated to program and made available for hand sign prediction. When user activates type function an area in display will be shown to user to show hand sign. After a short recognition process, the image of this area will be sent to the artificial intelligence and the letter to be determined by the artificial intelligence will be written in the most recent input field on the computer.

