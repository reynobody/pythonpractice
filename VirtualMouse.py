import cv2
import numpy as np
import handTrackingModule as htm
import time
import autopy
import math

##
wCam = 1080
hCam = 720
##
wBox = 640
hBox = 360
##
smoothen = 2
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
wScr, hScr = autopy.screen.size()

# print(wCam,hCam)
# print(wScr, hScr)

detector = htm.handDetector()

while True:
    success, img = cap.read()
    img = detector.findHands(img)

    # Draw mouse box
    cv2.rectangle(img, (200, 40), (200+wBox, 40+hBox), (255, 0, 0), 5)

    # Find tips of pointer and middle
    lmlist = detector.findPosition(img)

    start = False
    if len(lmlist) != 0:
        point = lmlist[8]
        if 200 < point[1] < 200+wBox  and 40 < point[2] < 40+hBox:
            start = True

    if len(lmlist) != 0 and start:

        # x and y coordinates for pointer
        x1, y1 = lmlist[8][1:]

        # x and y coordinates for thumb
        x2, y2 = lmlist[4][1:]

        # x and y coordinates for pinky
        x3, y3 = lmlist[20][1:]

        # x and y coordinates for middle
        x4, y4 = lmlist[12][1:]

        # check which fingers are up (wont do)
        # fingers = detector.fingersUp()
        # print(fingers)
        # only index finger moving mode (wont do)
        # if fingers[1]==1 and fingers[2]==0

        # convert coordinates
        x1b = np.interp(x1, (200,wBox), (0,wScr))
        y1b = np.interp(y1, (40,hBox), (0,hScr))

        # clocX = plocX + (x1b-plocX)/smoothen
        # clocY = plocY + (y1b-plocY)/smoothen

        # move the mouse
        autopy.mouse.move(wScr-x1b,y1b)
        cv2.circle(img, (x1,y1), 10, (255,255,0), cv2.FILLED)

        # update positions
        # plocX, plocY = clocX, clocY

        # find length between both thumb and pinky
        leftlength = math.hypot(x3 - x2, y3 - y2)

        # Draw line between thumb and pinky
        # cv2.line(img, (x2,y2), (x3,y3), (0,0,0), 1)
        if leftlength > 20:
            cv2.circle(img, ((x2+x3)//2, (y2+y3)//2), 5, (0,0,255))
        else:
            cv2.circle(img, ((x2 + x3) // 2, (y2 + y3) // 2), 5, (0, 255, 0))
            # Perform click
            autopy.mouse.click()

        # find length between thumb and middle
        rightlength = math.hypot(x4-x2, y4-y2)
        if rightlength > 20:
            cv2.circle(img, ((x2 + x4) // 2, (y2 + y4) // 2), 5, (0, 0, 255))
        else:
            cv2.circle(img, ((x2 + x4) // 2, (y2 + y4) // 2), 5, (0, 255, 0))
            # Perform toggle
            rclick = autopy.mouse.Button.RIGHT
            autopy.mouse.click(rclick)


    cv2.imshow("Image", img)
    cv2.waitKey(1)