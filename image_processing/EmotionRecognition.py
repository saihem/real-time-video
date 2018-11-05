import cv2
from keras.models import load_model
import numpy as np

from face_classification.src.utils.datasets import get_labels
from face_classification.src.utils.preprocessor import preprocess_input


def get_emotions_faces(image, face_bounding_boxes):
    recognized_emotions = []

    emotion_model_path = './face_classification/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_labels = get_labels('fer2013')

    emotion_classifier = load_model(emotion_model_path, compile=False)

    emotion_target_size = emotion_classifier.input_shape[1:3]

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    for face_coordinates in face_bounding_boxes:
        # x1, x2, y1, y2 = apply_offsets(face_coordinates, gender_offsets)

        gray_face = gray_image[face_coordinates[0]:face_coordinates[2], face_coordinates[3]:face_coordinates[1]]

        try:
            gray_face = cv2.resize(gray_face, emotion_target_size)
        except:
            continue

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
        emotion_text = emotion_labels[emotion_label_arg]

        recognized_emotions.append((emotion_text, face_coordinates))

    return recognized_emotions
