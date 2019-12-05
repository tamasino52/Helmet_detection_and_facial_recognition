import face_recognition
from PIL import Image, ImageDraw
import argparse
import os
import cv2 as cv
import camera
import face_recog
import numpy as np
import helmet_detection as helmet

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

# Main Code
if __name__ == "__main__":
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

    # --image option process
    if args.image:
        helmet = helmet.helmet_detection()
        face_recog = face_recog.FaceRecog(train_path)
        for img in os.listdir(test_path):
            # Extract unknown image list from directory
            img_path = test_path + '/' + img
            image_file = cv.imread(img_path)
            small_frame = cv.resize(image_file, (0, 0), fx=0.25, fy=0.25)

            face_recog_result = face_recog.get_frame(small_frame)
            helmet_result = helmet.get_detection(frame=small_frame, copy_frame=face_recog_result)

            # show the frame
            cv.imshow(winName, helmet_result)
            key = cv.waitKey(2000) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

    # --image option process
    elif args.video:
        # Get known image from train_path
        helmet = helmet.helmet_detection()
        cam = camera.VideoCamera(test_path)
        face_recog = face_recog.FaceRecog(train_path)

        while True:
            frame = cam.get_frame()
            frame = cv.resize(frame, dsize=(640, 480), interpolation=cv.INTER_AREA)

            face_recog_result = face_recog.get_frame(frame)
            helmet_result = helmet.get_detection(frame, face_recog_result)

            # show the frame
            cv.imshow(winName, helmet_result)
            key = cv.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # do a bit of cleanup
        cv.destroyAllWindows()
        print('Finish')
        exit()

    # --camera option process
    elif args.camera:
        # Get known image from train_path
        helmet = helmet.helmet_detection()
        cam = camera.VideoCamera(test_path)
        face_recog = face_recog.FaceRecog(train_path)

        while True:
            frame = cam.get_frame()

            face_recog_result = face_recog.get_frame(frame)
            helmet_result = helmet.get_detection(frame, face_recog_result)

            # show the frame
            cv.imshow(winName, helmet_result)
            key = cv.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # do a bit of cleanup
        cv.destroyAllWindows()
        print('Finish')
        exit()