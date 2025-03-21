# Importing modules
import Hand_tracking_module as htm
import cv2
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time
import os
from pathlib import Path
import image_handling as ih

# defining the main function
def main(images_path: str, 
         video_save_path: str, 
         video_name: str, 
         del_images_after: bool):

    cap = cv2.VideoCapture(0) # creating image capturing object

    detector = htm.hand_detector() # creating hand detection object

    run = True # defining run object

    pTime, cTime = 0, 0 # creating time objects for FPS tracker

    # defining some colors
    color_blue = (255, 150, 0)
    color_white = (255,255,255)
    color_green = (0, 255, 0)

    count = 0 # defining count object

    handler = ih.file_handling() # creating handler object

    finger_points = [4,8] # points to track

    path = images_path # creating path object

    # running while loop
    while run and cap.grab():

        ret, img = cap.read() # reading image
        img = cv2.flip(img, 1) # flipping image

        if ret:

            img, _ = detector.find_hands(img, 
                                         draw=False) # detecting hands

            datapoints = detector.track_pos(img, 
                                            track_points= finger_points) # tracking points 
            
            # if hands are being detected running operations
            if len(datapoints) > 0:
                
                # tracking x and y points
                x0, y0 = datapoints[0][1], datapoints[0][2] 
                x1, y1 = datapoints[1][1], datapoints[1][2]

                # calculating difference between points
                delta_x, delta_y = x1-x0, y1-y0

                # calculating center point between both points
                cx, cy = int((x0+x1)/2), int((y0+y1)/2)

                # calculating line length
                line_length = int(np.hypot(delta_x, delta_y))

                # defining condition for line length
                if line_length < 5:
                    cv2.circle(img, (cx, cy), 5, color_green, -1)

                # drawing on the image
                else:
                    cv2.circle(img, (x0, y0), 5, color_blue, -1)
                    cv2.circle(img, (x1, y1), 5, color_blue, -1)
                    cv2.line(img, (x0, y0), (x1, y1), color_blue, 2)
                    cv2.circle(img, (cx, cy), 5, color_white, -1)

                # initialising objects to control volume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

                # defining min and max volume
                minVol = -65.25
                maxVol = 0.0

                # defining line parameters
                line_magnitude = line_length
                line_min = 10
                line_max = 130

                # interpolating values for smooth operations
                # line length is interpolated between volume values
                # volume value is interpolated between 0-100
                # volume bar status is interpolated between values chosen accordingly to draw on the display
                line_length = np.interp(int(line_magnitude), [line_min, line_max], [minVol, maxVol])
                vol_current = np.interp(line_length, [minVol, maxVol], [0, 100])
                vol_bar_status = np.interp(int(vol_current), [0,100], [250, 70])

                vol_percent = f'Volume: {int(vol_current)}%' # defining volume percentage text

                # drawing on the image
                cv2.rectangle(img, (50,70), (70, 250), color_green, 2)
                cv2.rectangle(img, (50, int(vol_bar_status)), (70, 250), color_green, -1)
                cv2.putText(img, vol_percent, (20, 280), cv2.FONT_HERSHEY_PLAIN, 1, color_green, 2)

                # controlling the master volume
                volume = interface.QueryInterface(IAudioEndpointVolume)
                volume.SetMasterVolumeLevel(int(line_length), None)

            # calculating the FPS
            cTime = time.time()
            fps = f'FPS: {int(1/(cTime-pTime))}'
            pTime = cTime

            cv2.putText(img, fps, (5, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2) # putting FPS on image

            # saving the images
            handler.save_images(save_path = path, 
                                img= img, 
                                counter = count) # saving images
            
            cv2.imshow('feed', img) # running the feed

            count += 1 # incrementing the count

        k = cv2.waitKey(1)
        if k == ord('q'):
            # generating video through images
            handler.img_to_video(images_path=path, 
                                video_save_path=video_save_path, 
                                file_name=video_name)
            
            if del_images_after:
                
                # getting individual image path
                images = Path(path)
                images = list(images.glob('*.jpg'))

                # deleting the images
                for image in images:
                    os.remove(image)

                print('Images deleted')
            
            run = False

# executiong the function
main(images_path= 'images_save_path', # save path for images
     video_save_path= 'video_path', # save path for video
     video_name='volume_ctrl', # video_name
     del_images_after=True) # if the user want to delete the images used for video generation afterwards
