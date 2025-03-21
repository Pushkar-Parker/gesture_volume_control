# Importing modules
import mediapipe as mp
import cv2

# creating hand detection class with its attributes
class hand_detector():

    # defining the initialisation function
    def __init__(self): 
                 
        self.mpHands = mp.solutions.hands # initiating the hands attribute
        self.hands = self.mpHands.Hands() # initiating the hands function
        self.mpDraw = mp.solutions.drawing_utils # initiating the drawing function

    # creating an attribute to track hands
    def find_hands(self, img, draw= True):
        
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # creating an instance for the RGB image
        self.results = self.hands.process(img) # creating an instance for the results

        hand_idx = 8
        # detecting the hands and drawing the points
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

            hand_idx = self.results.multi_handedness[0].classification[0].index

        return img, hand_idx
    
    # tracking the position of specified points
    def track_pos(self, img, track_points: list):

        h, w, _ = img.shape

        LmList = []

        if self.results.multi_hand_landmarks:
            
            for handLms in self.results.multi_hand_landmarks:
                
                for id, lm in enumerate(handLms.landmark):
                    
                    if id in track_points:
                        
                        cx, cy = int(lm.x*w), int(lm.y*h)

                        LmList.append([id, cx, cy])
                        
                        if len(LmList) > len(track_points):
                            LmList.pop(0)

        return LmList
    

    # counting fingers
    def finger_count(self, img, points: list, hand_index: int, draw= True):
        
        color_green = (0, 255, 0) 
        fingers, thumb = [], []
        for i in range(len(points)):
            xi, yi = points[i][1], points[i][2]
            
            if i %2 == 1:
                if points[i][0] == 4:
                    if hand_index == 1:
                        if (points[i][1] - points[i+1][1]) < 0:
                            
                            thumb.append(points[i][0])
                            if draw:
                                cv2.circle(img, (xi,yi), 10, color_green, 2)

                    elif hand_index != 1:
                        if (points[i][1] - points[i+1][1]) > 25:
                            
                            thumb.append(points[i][0])
                            if draw:
                                cv2.circle(img, (xi,yi), 10, color_green, 2)

                else:
                    if (points[i][2] - points[i-1][2]) < -20:

                        fingers.append(points[i][0])
                        if draw:
                            cv2.circle(img, (xi,yi), 10, color_green, 2)

        return [fingers, thumb]
