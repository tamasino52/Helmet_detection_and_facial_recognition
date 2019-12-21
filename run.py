import face_recognition
from PIL import Image, ImageDraw
import argparse
import os
import cv2 as cv
import camera
import face_recog
import numpy as np
import helmet_detection as helmet
import DBmanager

def isOverlap(r1, r2):
    (r1x, r1y, r1w, r1h) = r1
    (r2x, r2y, r2w, r2h) = r2
    if r1x > r2x + r2w or r1x + r1w < r2x or r1y > r2y + r2h or r1y + r1h < r2y:
        return False
    return True

def display_result(frame, helmet_outs, face_outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    confThreshold = 0.5
    nmsThreshold = 0.4
    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    for out in helmet_outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)

    # Display the results
    for (top, right, bottom, left), name in face_outs:
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        overlap = False
        # Compare to existing helmet output area
        for i in indices:
            if overlap is True:
                break
            i = i[0]
            helmet_box = boxes[i]
            overlap = isOverlap(
                (helmet_box[0], helmet_box[1], helmet_box[2], helmet_box[3]),
                (left, top, right - left, bottom-top))

        # if there is overlap, then change box color
        ID = DBmanager.GetIDByName(name)[0]
        if overlap is True:
            DBmanager.UpdateRecent(ID)
            box_color = (0, 0, 255)
        else:
            DBmanager.AddWarnings(ID)
            box_color = (255, 0, 0)

        # Draw a box around the face
        cv.rectangle(frame, (left, top), (right, bottom), box_color, 2)

        # Draw a label with a name below the face
        cv.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv.FILLED)
        font = cv.FONT_HERSHEY_DUPLEX
        cv.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    return frame

# Main Code
if __name__ == "__main__":
    # Define args property
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--camera', action="store_true",
                       help='Camera Mode : Program get test image from camera on realtime')
    group.add_argument('-v', '--video', action="store_true",
                       help='Video Mode : Program get test image from video')
    group.add_argument('-i', '--image', action="store_true",
                       help='Image Mode : Program get test image from image')
    parser.add_argument('--train', default='./img/knowns',
                        help='Input training image-set path')
    parser.add_argument('--test', default='./img/unknowns',
                        help='Input test image-set path or video path or web-cam number.')
    args = parser.parse_args()

    # Initialize Some Variables
    train_path = []
    test_path = []

    # Input Parameter Adequacy Check
    if args.camera:
        print('Camera Mode On')
        # Only existed path is allowed
        assert os.path.exists(args.train)
        print('Train Path :: ', args.train)
        train_path = args.train
        # Default Camera number is 0
        try:
            test_path = int(args.test)
        except ValueError:
            test_path = 0
        print('Camera Number :: ', test_path)

    elif args.video:
        print('Video Mode On')
        # Only existed path is allowed
        assert os.path.exists(args.train)
        print('Train Path :: ', args.train)
        train_path = args.train
        assert os.path.exists(args.test)
        print('Test Video :: ', args.test)
        test_path = args.test

    elif args.image:
        print('Image Mode On')
        # Only existed path is allowed
        assert os.path.exists(args.train)
        print('Train Path :: ', args.train)
        train_path = args.train
        assert os.path.exists(args.test)
        print('Test Path :: ', args.test)
        test_path = args.test

    # Set window
    winName = 'Frame'
    cv.namedWindow(winName, cv.WINDOW_NORMAL)

    # Set DB
    DBmanager = DBmanager.DBmanager("log.db")
    DBmanager.ShowAllWorker()

    # --image option process
    if args.image:
        helmet = helmet.helmet_detection()
        face_recog = face_recog.FaceRecog(train_path)
        for img in os.listdir(test_path):
            # Extract unknown image list from directory
            img_path = test_path + '/' + img
            image_file = cv.imread(img_path)
            small_frame = cv.resize(image_file, (0, 0), fx=0.25, fy=0.25)

            face_recog_outs = face_recog.get_box(frame)
            helmet_result, helmet_outs = helmet.get_detection(frame)
            frame = display_result(frame, helmet_outs, face_recog_outs)

            # show the frame
            cv.imshow(winName, frame)
            key = cv.waitKey(2000) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

    # --camera / --video option process
    elif args.video or args.camera:
        # Get known image from train_path
        helmet = helmet.helmet_detection()
        cam = camera.VideoCamera(test_path)
        face_recog = face_recog.FaceRecog(train_path)

        while True:
            frame = cam.get_frame()
            frame = cv.resize(frame, dsize=(640, 480), interpolation=cv.INTER_AREA)

            face_recog_outs = face_recog.get_box(frame)
            helmet_result, helmet_outs = helmet.get_detection(frame)
            frame = display_result(frame, helmet_outs, face_recog_outs)
            # show the frame
            cv.imshow(winName, helmet_result)
            key = cv.waitKey(1) & 0xFF

            os.system('cls')
            DBmanager.ShowAllWorker()
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # do a bit of cleanup
        cv.destroyAllWindows()
        print('Finish')
        exit()

# End