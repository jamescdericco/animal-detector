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

app.logger.info("Initializing server...")


def get_required_env(var: str) -> str:
    value = os.getenv(var)
    if value is None:
        raise ValueError(f"Environment variable {var} is not defined.")

    return value


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = get_required_env("TWILIO_ACCOUNT_SID")
auth_token = get_required_env("TWILIO_AUTH_TOKEN")
twilio_phone_number = get_required_env("TWILIO_PHONE_NUMBER")


# NOTIFY_TXT_PHONE_NUMBERS is a comma separated list of ten digit phone numbers in E.164 format like '+12345678901'
notify_txt_phone_numbers = os.getenv("NOTIFY_TXT_PHONE_NUMBERS")
notify_txt_phone_numbers_list = (
    notify_txt_phone_numbers.split(",") if notify_txt_phone_numbers is not None else []
)

print(
    f"NOTIFY_TXT_PHONE_NUMBERS has {len(notify_txt_phone_numbers_list)} phone numbers"
)

client = Client(account_sid, auth_token)

# Tracks the time of the most recent high confidence detection for an animal
# to support detection cooldown
# Key: Prediction, Value: Timestamp (seconds)
detection_times = dict()

# Seconds until a new detection triggers a new notification
# following a previous notification for the same animal
detection_cooldown_seconds = 30 * 60

current_frame_datetime_utc = None
current_frame_img = None

animal_log_csv_filename = "animal_log.csv"

# Name of a model prediction where no animals are detected
empty_label = "empty"

# Do not notify contacts when the model predicts any of these animals (non-empty, empty is already ignored)
# these detections will still be logged into the `animal_log_csv_filename` file
do_not_notify_for_animals_set = {"squirrel", "jacky"}


def send_txt(phone: str, message: str):
    app.logger.info(f"sending txt to {phone} with message {message}")
    message = client.messages.create(body=message, from_=twilio_phone_number, to=phone)
    app.logger.info(message.body)


for phone_number in notify_txt_phone_numbers_list:
    send_txt(phone_number, "server is starting...")


def log_detection(animal: str, time: datetime):
    """Record the detection of animals to a CSV spreadsheet."""
    with open(animal_log_csv_filename, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write the animal and time as a new row
        writer.writerow([animal, time.strftime("%Y-%m-%dT%H:%M:%S")])


# Initialize the image classification model
learner = load_animal_detector_learner()


def handle_detection(
    prediction: str,
    confidence: float,
    frame_datetime: datetime,
    previous_prediction: str,
):
    """Notifies contacts about detection (if not in `do_not_notify_for_animals_set`) and add an entry to the `animal_log_csv_filename` file."""
    if prediction == empty_label:
        return

    if (
        confidence > 0.9
        and (previous_prediction == prediction or previous_prediction == empty_label)
        and (
            prediction not in detection_times
            or (frame_datetime - detection_times[prediction]).seconds
            > detection_cooldown_seconds
        )
    ):
        detection_times[prediction] = frame_datetime

        log_detection(prediction, frame_datetime)

        if prediction not in do_not_notify_for_animals_set:
            for phone_number in notify_txt_phone_numbers_list:
                send_txt(
                    phone_number,
                    f"At {frame_datetime} detected {prediction} {(confidence * 100):.0f}%",
                )


@app.route("/")
def home():
    return jsonify({"Title": "Animal Detection Server"})


# Prediction for the frame before the current one
previous_prediction = None


@app.post("/cat-food-cam/frame")
def update_frame_cat_food_cam():
    global current_frame_datetime_utc
    global current_frame_img
    global previous_prediction

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

    handle_detection(prediction, confidence, frame_datetime_utc, previous_prediction)

    previous_prediction = prediction

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
