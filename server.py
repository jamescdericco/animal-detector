from datetime import datetime, timezone
from io import BytesIO
import os
from flask import Flask, Response, jsonify, request
from fastai.vision.all import *
import logging
from logging.handlers import RotatingFileHandler
import time
from twilio.rest import Client

from animal_detector import load_animal_detector_learner

app = Flask(__name__)

# Set up logging to a file
file_handler = RotatingFileHandler("server.log", maxBytes=1000000, backupCount=100)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Initialize the image classification model
learner = load_animal_detector_learner()

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

# NOTIFY_TXT_PHONE_NUMBERS is a comma separated list of ten digit phone numbers in E.164 format like '+12345678901'
notify_txt_phone_numbers = os.getenv("NOTIFY_TXT_PHONE_NUMBERS")
notify_txt_phone_numbers_list = (
    notify_txt_phone_numbers.split(",") if notify_txt_phone_numbers is not None else []
)

client = Client(account_sid, auth_token)

# Key: Label, Value: Timestamp (seconds)
detection_times = dict()
current_frame_datetime_utc = None
current_frame_img = None

ignore_prediction_set = {"empty", "squirrel"}


def send_txt(phone, message):
    app.logger.info(f"sending txt to {phone} with message {message}")

    message = client.messages.create(body=message, from_=twilio_phone_number, to=phone)

    app.logger.info(message.body)


def notify_animal_detected(prediction, confidence, frame_datetime):
    confidence_percent = confidence * 100

    if prediction in ignore_prediction_set:
        return

    if (
        prediction not in detection_times
        or (frame_datetime - detection_times[prediction]).seconds > 30 * 60
    ):
        detection_times[prediction] = frame_datetime
        for phone_number in notify_txt_phone_numbers_list:
            send_txt(
                phone_number,
                f"At {frame_datetime} detected {prediction} {confidence_percent:.2f}%",
            )


@app.route("/")
def home():
    return jsonify({"Title": "Animal Detection Server"})


@app.post("/cat-food-cam/frame")
def update_frame_cat_food_cam():
    global current_frame_datetime_utc
    global current_frame_img

    start_time_request = time.time()
    if "image" not in request.files or "timestamp" not in request.form:
        return jsonify({"error": "Missing 'image' or 'timestamp'"}), 400

    # Get the image file and timestamp
    image = request.files["image"]
    timestamp = request.form["timestamp"]
    frame_datetime_utc = datetime.fromtimestamp(int(timestamp)).astimezone(timezone.utc)
    current_frame_datetime_utc = frame_datetime_utc

    # Ensure the image file is provided
    if image.filename == "":
        return jsonify({"error": "No file uploaded"}), 400

    img = PILImage.create(image.stream)
    current_frame_img = img

    start_time_predict = time.time()
    prediction, prediction_index, probabilities = learner.predict(img)
    confidence = probabilities[prediction_index]
    end_time_predict = time.time()

    img.save(
        f"server/frame_time-utc-{frame_datetime_utc.strftime('%Y-%m-%dT%H-%M-%S')}_prediction-{prediction}_confidence-percent-{int(confidence*100):2d}.png"
    )

    if confidence > 0.9:
        notify_animal_detected(prediction, confidence, frame_datetime_utc)

    end_time_request = time.time()
    app.logger.info(
        f"Performance Timing Seconds: Request ({end_time_request - start_time_request:.3f}), Predict ({end_time_predict - start_time_predict:.3f})"
    )
    return jsonify({"message": "Frame uploaded successfully"}), 200


@app.get("/cat-food-cam/frame/time")
def get_frame_time():
    return jsonify(
        {
            "Time": (
                str(current_frame_datetime_utc)
                if current_frame_datetime_utc is not None
                else "NA"
            )
        }
    )


@app.get("/cat-food-cam/frame")
def get_frame_img():
    # Convert the PIL image to a byte stream
    img_io = BytesIO()
    current_frame_img.save(img_io, "PNG")  # Or 'PNG' depending on the image format
    img_io.seek(0)

    # Return the byte stream as a response with the correct MIME type
    return Response(img_io, mimetype="image/png")


if __name__ == "__main__":
    app.run()
