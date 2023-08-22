import cv2
import pickle

# Check for previously selected parking spots
try:
    with open("parkingSlotPosition", "rb") as f:
        posList = pickle.load(f)
except:
    posList = []

# ROI(Parking Space) width and height
width, height = 107, 48


def mouseClick(events, x, y, flags, param):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)

    with open("parkingSlotPosition", "wb") as f:
        pickle.dump(posList, f)


if __name__ == "__main__":
    while True:
        img = cv2.imread("../flask/dataset/carParkImg.png")
        for pos in posList:
            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.setMouseCallback("Image", mouseClick)
        cv2.waitKey(1)
        # if (cv2.waitKey(0) & 0xFF) == ord("q"):
        #     cv2.destroyAllWindows()
        #     break
