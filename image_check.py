import cv2
import sys
import time
import zipfile
import requests
import matplotlib.pyplot as plt
import numpy as np
import datetime
import threading
import time

output_file = 'outp.avi'
zipped_file = 'test.zip'

try:
    gap_time = int(sys.argv[1])
except IndexError:
    gap_time = None


def send_frame(endpoint_uri, file):
    with open(file, 'rb') as f:
        try:
            r = requests.post(endpoint_uri, files={'file': f})
            return r
        except Exception as e:
            print(e)


def make_graph(results):
    labels = list(results['answer'].keys())

    values = np.asarray(list(results['answer'].values()))
    values = values.astype(float)
    values = values * 100

    fig, ax = plt.subplots()
    y_pos = np.arange(len(labels))

    ax.bar(y_pos, values, align='center', alpha=0.5)
    plt.xticks(y_pos, labels)
    ax.set_ylim(0, 100)

    for i, v in enumerate(values):
        plt.text(i - 0.2, v + 1, str(round(v, 2)) + '%', color='blue', fontsize=14)

    plt.ylabel('Percentage')
    title = 'Image Recognition %s' % (datetime.datetime.now().time())
    plt.title(title)
    file = '%s.png' % title
    plt.savefig(file)
    plt.ion()
   # plt.show(block=False)
    return plt


def stream_video_image(gap):
    # Initializes webcam and for a frequency of the <gap_time> sends zip of images to an endpoint
    cap = cv2.VideoCapture(0)
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 25, (1920, 1080))
    start_time = int(round(time.time()))
    while (cap.isOpened()):
        ret, frame = cap.read()
        out.write(frame)
        cv2.imshow('frame', frame)
        cv2.waitKey()
        current_time = int(round(time.time()))
        seconds = current_time - start_time
        if seconds % gap == 0:
            image_file = "frame-%d.jpeg" % seconds
            cv2.imwrite(image_file, frame)
            yield image_file
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break
    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    # return output_file


def get_match(response):
    matched = (None, 0)
    for item, match_rate in response['answer'].items():
        if match_rate * 100 > 50:  # we want 75 match rate ***MAME THIS sure is right
            matched = (item, match_rate * 100)
    return matched


def check_image(gap=2, stop_time=5, show_image=False):
    start = int(round(time.time()))
    for image_file in stream_video_image(gap):
        response = send_frame('https://tensorflowwaiter-aserecruitfy19.uscom-central-1.oraclecloud.com/tensorflow',
                              image_file)
        try:
            if response.status_code == 200:
                make_graph(response.json())
                yield get_match(response.json())
            if stop_time <= int(round(time.time())) - start:
                break
        except AttributeError:
            pass


def api_return_gen(gap=10, stop_time=None):
    matches = {}
    for resp in check_image(gap=gap, stop_time=stop_time):
        matches[datetime.datetime.now().time()] = resp
    return matches

mats = api_return_gen(10, 120)
print(mats)
