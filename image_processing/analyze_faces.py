import sys
import face_recognition
import face_recognition.face_recognition_cli as cli
import json
import cv2

from .EmotionRecognition import get_emotions_faces
from .FaceRecognition import get_names_faces


def analyze(images=None):
    random_faces_path = "./unknown/test.jpg"
    known_faces_path = "./known"

    # random_faces_image = face_recognition.load_image_file(random_faces_path)
    known_names, known_face_encodings = cli.scan_known_people(known_faces_path)

    image = images[0]
    random_faces_image_read = cv2.imread(image, cv2.IMREAD_COLOR)
    random_faces_image = random_faces_image_read.copy()[:, :, ::-1]
    recognized_faces = get_names_faces(random_faces_image, known_names, known_face_encodings)

    if not recognized_faces:
        return {}
    name_emotion = {}

    if recognized_faces is None:
        print(name_emotion)

    face_bounding_boxes = []

    for face_name in recognized_faces:
        face_bounding_boxes.append(face_name[1])

    try:
        emotion_bounding_boxes = get_emotions_faces(random_faces_image_read, face_bounding_boxes)
    except:
        return {}

    for name_bounding_box, emotion_bounding_box in zip(recognized_faces, emotion_bounding_boxes):
        name_emotion[name_bounding_box[0]] = emotion_bounding_box[0]

    return name_emotion


def video():
    cap = cv2.VideoCapture(0)

    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        rgb_frame = frame.copy()[:, :, ::-1]

        # Display the resulting frame
        cv2.imshow('frame', frame)

        wait = cv2.waitKey(1) & 0xFF

        if wait == ord('w'):
            analyze(rgb_frame)
        elif wait == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def main():
    # analyze()
    video()


if __name__ == "__main__":
    main()
