import ibm_db
from flask import Flask, render_template, request, session
import cv2
import pickle
import cvzone
import numpy as np
import re

# Creating Flask App
app = Flask(__name__)
app.secret_key = 'x'
# Establishing DB Connection
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=bxh70612;PWD=5Rsm7faIKZssJ3ef;", "", "")
print(" * Connected to Db2")


@app.route('/')
def project():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/model')
def model():
    return render_template('model.html')


@app.route('/log')
def log():
    return render_template('login.html')


@app.route('/reg')
def reg():
    return render_template('register.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    msg = ""
    if request.method == 'POST':
        print(request.form)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * FROM REGISTER WHERE name= ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = "Account already exists!"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid Email Address!'
        else:
            insert_sql = "INSERT INTO REGISTER VALUES (?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = "You have successfully registered !"
    return render_template("register.html", msg=msg)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        e=account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['EMAIL']
            session['email'] = account['EMAIL']
            return render_template('model.html')
        else:
            msg = "Incorrect Email/Password"
            return render_template('login.html', msg=msg)
    else:
        return render_template("login.html")


@app.route('/predict_live')
def predict_live():
    # ROI(Parking Space) width and height
    width, height = 107, 48
    # Video Capture
    cap = cv2.VideoCapture("dataset/carParkingInput.mp4")
    # Loading previously selected parking slots
    with open("dataset/parkingSlotPosition", "rb") as f:
        posList = pickle.load(f)

    def checkParkingSpace(imgPro):
        spaceCounter = 0
        # Crop selected parking slots
        for pos in posList:
            x, y = pos
            imgCrop = imgPro[y:y + height, x:x + width]

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
        cvzone.putTextRect(img, f"Free: {spaceCounter}/{len(posList)}", (100, 50), scale=3, thickness=5, offset=20,
                           colorR=(0, 200, 0))

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
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25,
                                             16)
        # median filter
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        # dilate
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        checkParkingSpace(imgDilate)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return render_template('model.html')


if __name__ == '__main__':
    app.run(debug=True)