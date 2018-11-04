from flask import Flask, render_template, Response, stream_with_context, jsonify
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
from .process_image import send_image
from .camera import stream_video
from . import app
from .models import alchemyencoder, Response as ModelResp, db
from sqlalchemy.orm import joinedload


@app.route('/')
def index():
    url = 'http://0.0.0.0:8000/start_camera'
    try:
        requests.get(url)
    except:
        pass
    return render_template('index.html')


def this_dev_stream():
    start_time = time.time()
    gap = 10
    while True:
        for frame in stream_video():
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + open(frame, 'rb').read() + b'\r\n\r\n')
            elapsed = round(time.time() - start_time)
            # # img = cv2.imdecode(np.frombuffer(msg.value, np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            if elapsed % gap == 0:
                image_bytes = io.BytesIO(open(frame, 'rb').read())
                send = multiprocessing.Process(target=send_image, args=(image_bytes, elapsed))
                send.daemon = True
                send.start()


# BELOW RUNS SCRIPT THAT STARTS IN VIDEO LOAD
def remote_stream(consumer):
    start_time = time.time()
    while True:
        time.clock()
        gap = 10
        for msg in consumer:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + msg.value + b'\r\n\r\n')
            # put everything below in an async function
            elapsed = time.time() - start_time
            # img = cv2.imdecode(np.frombuffer(msg.value, np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            # if elapsed % gap == 0:
            image_bytes = io.BytesIO(msg.value)
            send = multiprocessing.Process(target=send_image, args=(image_bytes, elapsed))
            send.daemon = True
            send.start()


@app.route('/video', methods=['GET'])
def video_feed():
    use_this_device = True
    # get this device stream
    if use_this_device:
        return Response(this_dev_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
    # get remote stream
    else:
        return Response(
            remote_stream(consumer=KafkaConsumer('video-stream', group_id='view', bootstrap_servers=['0.0.0.0:9092'])),
            mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/resps', methods=['GET'])
def get_response():
    mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=2)
    resp = {}
    for r in list(db.session.query(ModelResp).options(joinedload(ModelResp.type)).filter(ModelResp.time <= mins_ago)):
        resp['time'] = r.time.strftime("%Y-%m-%d %H:%M:%S")
        resp['type'] = r.type.name
        resp['response'] = r.response
    return jsonify(resp)
    # return json.dumps([dict(r) for r in responses], default=alchemyencoder)


@app.route('/api/imgs', methods=['POST'])
def post_img():
    resp = {'file':datetime.datetime.now()}
    return jsonify(resp)