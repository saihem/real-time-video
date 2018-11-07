import sys
import cv2
import face_recognition
import glob
import os
import re
from .NametagRecognition import get_nametag_text
from .FaceRecognition import get_cropped_face

def store(images=None):

    face_nametag_path = "./nametag_samples/"
    known_faces_path = "./known/"


    if not os.path.exists(known_faces_path):
        os.makedirs(known_faces_path, 0o777)

    # face_nametag_image = face_recognition.load_image_file(face_nametag_path)

    nametag_text_cropped_face = {}
    cropped_face = None
    nametag_text = None
    for image in images:
        face_nametag_image = cv2.imread(image, cv2.IMREAD_COLOR)
        # find name and face
        try:
            name = get_nametag_text(face_nametag_image).strip()
        except AttributeError:
            continue
        if name is not None and len(name) >= 3 and not re.match(r'[^A-Za-z0-9]', name):
            count = 1
            if name in nametag_text_cropped_face:
                count = nametag_text_cropped_face[name][0] + 1
            nametag_text_cropped_face[name] = (count, face_nametag_image)


    # save name and face as file
    names = []
    count = 0
    for name, count_array in nametag_text_cropped_face.items():
        if count_array[0] > count:
            names = []
            names.append(name)
            count = count_array[0]
            continue
        if count_array[0] ==  count:
            names.append(name)
    if not names:
        return False
    nametag_text = max(names, key=len)
    cropped_face = get_cropped_face(nametag_text_cropped_face[nametag_text][1])

    if nametag_text is None and cropped_face is None:
        print("name and face not found")
    elif nametag_text is None:
        print("name not found")
    elif cropped_face is None:
        print("face not found")
    else:
        filename = os.path.join(known_faces_path,f"{nametag_text}.jpg")
        counter = 1

        # if same name already stored, add counter
        while os.path.exists(filename):
            filename = os.path.join(known_faces_path,f"{nametag_text}{str(counter)}.jpg")
            counter += 1

        cv2.imwrite(filename, cropped_face)
        print(filename)
    return True


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
            store(rgb_frame)
        elif wait == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def main():
    # store()
    video()

    # if cv2.waitKey(1) & 0xFF == ord('w'):
        #     store(rgb_frame)


        # if cv2.waitKey(2) and 0xFF == ord('q'):
        #     break


if __name__ == "__main__":
    main()
