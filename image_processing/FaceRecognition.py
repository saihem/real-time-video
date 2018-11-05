from PIL import Image
import face_recognition
import os
import glob
import PIL.Image
import numpy as np

def remove_face_image(file_name, folder_path="./known/"):
    os.remove(folder_path + file_name)


def remove_all_face_images(folder_path="./known/"):
    files = glob.glob(folder_path + "*")
    for f in files:
        os.remove(f)


def get_cropped_face(face_nametag_image):
    # original dimensions of the image
    (height, width) = face_nametag_image.shape[:2]

    # convert image to rgb
    rgb_frame = face_nametag_image.copy()[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_frame)

    if not face_locations:
        return None

    # find largest face bounding box
    areas = {(right - left) * (bottom - top): (top, right, bottom, left) for (top, right, bottom, left) in
             face_locations}
    biggest_rect = max(list(areas.keys()))
    top, right, bottom, left = areas[biggest_rect]
    # cv2.rectangle(unknown_image, (left, top), (right, bottom), (0, 0, 255), 2)

    scale = int(((bottom - top) + (right - left)) / 2 * .2)

    scaled_top = top - scale
    scaled_right = right + scale
    scaled_bottom = bottom + scale
    scaled_left = left - scale

    # use previous coordinates if scaled image out of bounds
    if scaled_top < 0:
        scaled_top = 0
    if scaled_right > width:
        scaled_right = width
    if scaled_bottom > height:
        scaled_bottom = height
    if scaled_left < 0:
        scaled_left = 0

    cropped_image = rgb_frame[scaled_top:scaled_bottom, scaled_left:scaled_right]

    return cropped_image


def get_names_faces(random_faces_image, known_names, known_face_encodings, tolerance=0.6):

    # Scale down image if it's giant so things run a little faster
    if max(random_faces_image.shape) > 1600:
        pil_img = PIL.Image.fromarray(random_faces_image)
        pil_img.thumbnail((1600, 1600), PIL.Image.LANCZOS)
        random_faces_image = np.array(pil_img)

    unknown_encodings = face_recognition.face_encodings(random_faces_image)
    unknown_locations = face_recognition.face_locations(random_faces_image)

    if not unknown_encodings:
        return None

    recognized_faces = []
    unrecognized_faces_counter = 0

    for index, unknown_encoding in enumerate(unknown_encodings):
        distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)

        if min(distances) <= tolerance:
            min_dist_pos = distances.argmin()
            recognized_faces.append((known_names[min_dist_pos], unknown_locations[index]))
        else:
            unrecognized_faces_counter+=1
            recognized_faces.append(("unrecognized_person" + str(unrecognized_faces_counter), unknown_locations[index]))

    return recognized_faces

