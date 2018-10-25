from flask import Flask, render_template, Response, stream_with_context
import requests
import datetime
import matplotlib.pyplot as plt
import numpy as np
import asyncio
import aiohttp
import socket
import cv2
import time
import io
import binascii
import os
import multiprocessing
from kafka import KafkaConsumer

from .config import create_app
from.process_image import send_image


config_name = os.getenv('FLASK_CONFIG')  # config name will be used in create_app
app = create_app('development')


@app.route('/')
def index():
    url = 'http://0.0.0.0:5000/start_camera'
    requests.get(url)
    return render_template('index.html')


# BELOW RUNS SCRIPT THAT STARTS IN VIDEO LOAD
def gen_yes(consumer):
    start_time = time.time()
    while True:
        time.clock()
        gap = 10
        stop_time = 20
        # executor = concurrent.futures.ThreadPoolExecutor(
        #     max_workers=3,
        # )
        # event_loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(event_loop)
        # event_loop = asyncio.get_event_loop()
        # try:
        #     future = [asyncio.ensure_future(check_image(gap=gap, stop_time=stop_time))]
        #     matches = loop.run_forever()
        # r = requests.get(url, stream=True)
        # yield r.iter_content(chunk_size=10 * 1024)
        # for frame in requests.get(url, stream=True):
        #     yield (b'--frame\r\n'
        #                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        # finally:
        #     event_loop.close()
        for msg in consumer:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + msg.value + b'\r\n\r\n')
            # put everything below in an async function
            elapsed = time.time()
            # img = cv2.imdecode(np.frombuffer(msg.value, np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            if elapsed % start_time == gap:
                image_bytes = io.BytesIO(msg.value)
                send = multiprocessing.Process(target=send_image, args=(image_bytes,))
                send.daemon = True
                send.start()


# @app.route('/video', methods=['GET'])
@app.route('/video')
def video_feed():
    # url = 'http://127.0.0.1:5000/'
    # return Response(gen_yes(url),
    #                 mimetype='multipart/x-mixed-replace; boundary=frame')
    # r = gen_yes(url)
    #  r = requests.get(url, stream=True)
    # return Response(r.iter_content(chunk_size=10 * 1024),
    #                content_type=r.headers['Content-Type'],
    #               mimetype='multipart/x-mixed-replace; boundary=frame')

    consumer = KafkaConsumer('video-stream', group_id='view', bootstrap_servers=['0.0.0.0:9092'])
    return Response(gen_yes(consumer=consumer),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000, threaded=True)


