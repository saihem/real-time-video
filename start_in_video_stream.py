import cv2
import time
import json
import io
import sys
from threading import Thread

from flask import Flask, request, Response, jsonify, stream_with_context
from flask_restful import Api, Resource
from kafka import SimpleProducer, SimpleClient, KafkaProducer, KafkaClient

# kafka = KafkaClient('localhost:9092')
producer = KafkaProducer(bootstrap_servers='localhost:9092')
# Assign a topic
topic = 'video-stream'

app = Flask(__name__)
api = Api(app)


class Wrapper(object):
    def __init__(self, gen):
        self._gen = gen
        self.called = []

    def __iter__(self):
        return self

    def close(self):
        self.called.append(42)

    def __next__(self):
        return next(self._gen)


def stream_video_image(gap=10, stop_time=40):
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
            # image_file = f"frame-{seconds}.jpeg"
            # cv2.imwrite(image_file, frame)
            # bytes_file = open(image_file, 'rb').read()
            ret, jpeg = cv2.imencode('.jpeg', frame)
            # Convert the image to bytes and send to kafka
            producer.send(topic, jpeg.tobytes())
            # To reduce CPU usage create sleep time of 0.2sec
            time.sleep(0.2)
            # yield json.loads(open(image_file, 'rb').read().readall().decode('utf-8'))
            if cv2.waitKey(1) and 0xFF == ord('q'):
                break
            if seconds > 120:
                break
    except:
        sys.exit(1)
    cap.release()
    out.release()
    cv2.destroyAllWindows()


# class Cam(Resource):
#     def get(self):
#         rv = Response(stream_video_image(), content_type='text/event-stream')
#         return rv, 200
#
#     @app.after_request
#     def after_request(response):
#         response.headers.add('Accept-Ranges', 'bytes')
#         return response

@app.route('/start_camera', methods=['GET'])
def start_camera():
    thread = Thread(target=stream_video_image)
    thread.daemon = True
    thread.start()
    return jsonify({"started": "started camera"})


# return Response(stream_with_context(Wrapper(stream_video_image())))


# api.add_resource(Cam, "/video_feed/")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000, threaded=True)
    # stream_video_image()
