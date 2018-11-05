import cv2
import time
import sys


def stream_video():
    # Initializes webcam and for a frequency of the <gap_time> sends zip of images to an endpoint
    cap = cv2.VideoCapture(0)
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 25, (1920, 1080))
    start_time = int(round(time.time()))
    try:
        while (True):
            grabbed, frame = cap.read()
            current_time = int(round(time.time()))
            out.write(frame)
            seconds = current_time - start_time
            if seconds >999:
                start_time = int(round(time.time()))
            image_file = f"frame-{seconds}.jpeg"
            cv2.imwrite(image_file, frame)
            yield image_file
            #yield open(image_file, 'rb').read()
            if cv2.waitKey(1) and 0xFF == ord('q'):
                break
            if seconds > 120:
                break
    except:
        sys.exit(1)
    cap.release()
    out.release()
    cv2.destroyAllWindows()