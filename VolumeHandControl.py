import cv2
import mediapipe as mp
import time
import numpy
import handTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

####
wCam, hCam = 720, 480
pTime = 0
####

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# Create object from handdetector class
detector = htm.handDetector(detectionCon=0.8)

# Import pycaw volume controlv
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volcur = volume.GetMasterVolumeLevel()
volrange = volume.GetVolumeRange()
minvol = volrange[0]
maxvol = volrange[1]

vol = 0

while True:
    success, img = cap.read()

    # Find hand and draw
    img = detector.findHands(img)

    # Find hand position
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        # Draw circles around thumb and pointer
        cv2.circle(img, (x1,y1), 5, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2,y2), 5, (255,0,255), cv2.FILLED)

        # Draw line between thumb and pointer
        cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 1)

        # Draw circle in the middle of the line
        cv2.circle(img, (cx,cy), 5, (255,0,255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)

        # Hand length range 0 -> 300, convert to volume range -65 -> 0
        vol = int(numpy.interp(length, [20,300], [minvol,maxvol]))
        volbar = numpy.interp(length, [20,300], [400,150])
        volper = numpy.interp(length, [20,300], [0,100])
        print(int(length), int(vol))

        if length < 100:
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
            # volume.SetMasterVolumeLevel(-60, None)
        elif length < 200:
            cv2.circle(img, (cx, cy), 5, (0, 255, 255), cv2.FILLED)
            # volume.SetMasterVolumeLevel(-45, None)
        elif length < 250:
            cv2.circle(img, (cx, cy), 5, (0, 165, 255), cv2.FILLED)
            # volume.SetMasterVolumeLevel(-30, None)
        else:
            cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
            # volume.SetMasterVolumeLevel(-50, None)

        # Create and draw volume bar
        cv2.rectangle(img, (50,150), (85,400), (0,255,0), 3)
        cv2.rectangle(img, (50,int(volbar)), (85,400), (0,255,0), cv2.FILLED)

        # Middle finger value and middle knuckle value
        print(lmList[12][2], lmList[9][2])
        midval = lmList[12][2] - lmList[9][2]

        # Cut off changing volume
        if midval <= 0:
            # Set volume on device
            volume.SetMasterVolumeLevel(vol, None)
            # Draw value of volume
            cv2.putText(img, f'{int(volper)}%', (40, 440), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
            volcur = volper
        else:
            cv2.putText(img, f'{int(volcur)}%', (40, 440), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
            False

        # if midval >= 0 and lmList[5][2] < lmList[0][2]:
        #     volume.SetMasterVolumeLevel(vol, None)
        # else:
        #     False


    # Set framerate
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    # Shows image and window name is "Img"
    cv2.putText(img, f'FPS: {int(fps)}', (40, 40), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,0), 3)
    cv2.imshow("Img", img)
    cv2.waitKey(1)