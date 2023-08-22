import cv2
import pickle
import cvzone
import numpy as np

# ROI(Parking Space) width and height
width, height = 107, 48
# Video Capture
cap = cv2.VideoCapture("dataset/carParkingInput.mp4")
# Loading previously selected parking slots
with open("parkingSlotPosition", "rb") as f:
    posList = pickle.load(f)


def checkParkingSpace(imgPro):
    spaceCounter = 0
    # Crop selected parking slots
    for pos in posList:
        x, y = pos
        imgCrop = imgPro[y:y+height, x:x+width]
        cv2.imshow(str(x*y), imgCrop)

        count = cv2.countNonZero(imgCrop)
        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2
        # Draw selected slots
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 5), scale=1.5, thickness=2, offset=0, colorR=color)
    cvzone.putTextRect(img, f"Free: {spaceCounter}/{len(posList)}", (100, 50), scale=3, thickness=5, offset=20, colorR=(0, 200, 0))


while True:
    # Loop video
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    # Read frames
    success, img = cap.read()

    # cvt to Grayscale
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # blur
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    # thresholding
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    # median filter
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    # dilate
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)

    cv2.imshow("Image", img)
    # cv2.imshow("GrayImage", imgGray)
    # cv2.imshow("BlurImage", imgBlur)
    # cv2.imshow("ThresholdImage", imgThreshold)
    # cv2.imshow("MedianImage", imgMedian)
    # cv2.imshow("DilateImage", imgDilate)
    cv2.waitKey(10)