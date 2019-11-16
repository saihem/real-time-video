from flask import Flask, render_template, Response, jsonify, flash, request, redirect, url_for, send_from_directory
import requests
import datetime
import matplotlib.pyplot as plt
import numpy as np
import asyncio
import socket
import cv2
import time
import io
import binascii
import os
import glob
from multiprocessing import Pool, Process, Queue
from kafka import KafkaConsumer
from .process_image import process_image, train_image
from .camera import stream_video
from . import app
from .models import db, Response as ModelResp
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from .config import ALLOWED_EXTENSIONS
from flask_cors import CORS, cross_origin
from sqlalchemy import desc

CORS(app, support_credentials=True)


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
    gap = 5
    while True:
        for frame in stream_video():
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + open(frame, 'rb').read() + b'\r\n\r\n')
            # elapsed = round(time.time() - start_time)
            # # img = cv2.imdecode(np.frombuffer(msg.value, np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            # if elapsed % gap == 0:
            #     image_bytes = io.BytesIO(open(frame, 'rb').read())
            #     send = Process(target=send_image, args=(image_bytes, elapsed))
            #     send.daemon = True
            #     send.start()


# Starts kafka consumer and receives bytes from remote stream
def remote_stream(consumer):
    start_time = time.time()
    while True:
        time.clock()
        gap = 10
        for msg in consumer:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + msg.value + b'\r\n\r\n')
            # elapsed = time.time() - start_time
            # img = cv2.imdecode(np.frombuffer(msg.value, np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            # if elapsed % gap == 0:
            #     image_bytes = io.BytesIO(msg.value)
            #     send = Process(target=process_image, args=(image_bytes, elapsed))
            #     send.daemon = True
            #     send.start()


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


#Queries latest responses
@app.route('/api/resps', methods=['GET'])
def get_response():
    emotion_emoji = {
        'neutral': "😐😶",
        'sad': "😢",
        'happy': "😀😁",
        'fear': "😱",
        'disgust': "😖🤮",
        'angry': "😡",
        'surprise': "😲🤯"
    }
    mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
    resp = []
    for r in list(
            db.session.query(ModelResp).options(joinedload(ModelResp.type)).filter(ModelResp.time >= mins_ago).order_by(
                    ModelResp.time.desc())):
        emoji = emotion_emoji.get(r.type.name, '')
        response_display = f"{r.response} {emoji}"
        resp.append({'time': r.time.strftime("%Y-%m-%d %H:%M:%S"),
                     'type': r.type.name,
                     'response': response_display})

    return jsonify(resp)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)
#
#
# @app.route('/api/imgs', methods=['POST'])
# @cross_origin(supports_credentials=True)
# def post_img():
#     resp = {}
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # if user does not select file, browser also
#         # submit an empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             file_path = url_for('uploaded_file',
#                                 filename=filename)
#             resp = {file_path: datetime.datetime.now()}
#             send = Process(target=process_image, args=(cv2.imread(file_path, cv2.IMREAD_COLOR),))
#             send.daemon = True
#             send.start()
#     return jsonify(resp)


def get_latest_image():
    list_of_images = glob.glob('frame-??.jpeg') + glob.glob('frame-?.jpeg') + glob.glob('frame-???.jpeg')
    latest_file_creation_time = os.path.getctime  # * means all if need specific format then *.csv
    files = []
    files.append(max(list_of_images, key=latest_file_creation_time))
    files.append(sorted(list_of_images, key=latest_file_creation_time)[-2])
    files.append(sorted(list_of_images, key=latest_file_creation_time)[-3])
    files.append(sorted(list_of_images, key=latest_file_creation_time)[-4])
    files.append(sorted(list_of_images, key=latest_file_creation_time)[-5])
    return files, max(list_of_images, key=latest_file_creation_time)


@app.route('/api/train', methods=['GET'])
def start_training():
    files, latest_file = get_latest_image()
    trained = train_image(files)
    data = {
        'API_KEY': 'one_hub',
        'addbbcode20': '0',
        'files': files,
        'message': 'alice-body',
        'mode': 'newtopic',
        'sid': '5b2e663a3d724cc873053e7ca0f59bd0',
    }
    train_url = 'http://localhost:8080/train'
    trained = requests.post(train_url, data=data)
    resp = [latest_file, trained, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    return jsonify(resp)

from .image_processing.EmotionRecognition import EmotionFace
em_face = EmotionFace()
pool = Pool(processes=4)
@app.route('/api/analyze', methods=['GET'])
def analyze():
    files, latest_file = get_latest_image()
    #q = Queue()
    # send = Process(target=analyze, args=(q,images))
    # send.start()
    # analysis = q.get()
    # send.join()
    analysis = pool.apply_async(process_image, args=(files, em_face))
    #analysis = process_image(files)
    resp = [latest_file, analysis.get(), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    return jsonify(resp)
