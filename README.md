# Animal Detector

Animal Detector is a camera system designed to identify specific cats by name, as well as squirrels and notify me when animals appear on camera so that I can provide them with fresh wet food or other care. The camera runs in a web browser on a smartphone that I placed inside of a cat food house. The camera regularly sends image frames to an animal detector server that uses an image classification algorithm to identify which animals, if any, are in the camera frame. If the algorithm is highly confident in its prediction, then the server will send me a notification, telling me which animal has visited the cat food house.

I trained an image classification deep learning model using camera images that this server collects, as well as images from a separate camera system. By default, the server saves all of the image frames it receives from the camera. I label these image frames by moving them into folders for each label, which are then used by my Kaggle notebook to train a new image classification model using fastai with PyTorch.

## Setup Server Conda Environment
The server requires a Linux operating system (this project was tested on Ubuntu 24.04 with the x86_64 architecture). Although the server uses a deep neural network model to do image classification, it does not use the GPU, as PyTorch is configured to run CPU-only for inference in `environment.yml`.

Install [miniconda](https://docs.anaconda.com/miniconda/)

Once you’ve copied this repository to your server, create the `animal_detector` conda environment, including Python and this project's dependencies.

```sh
conda env create -f environment.yml
```

## Setup the Image Classification Model

Download the PyTorch model from https://www.kaggle.com/models/jamesdericco/animal_detector_model/. Save this file as `export.pkl` in a `model` subdirectory of the project root.

This model was generated in the Kaggle notebook https://www.kaggle.com/code/jamesdericco/animal-detector. The data used to train the model is available at https://www.kaggle.com/datasets/jamesdericco/cat-food-cam-20241006/.

## Running the Server
To run the server, ensure the following environment variables are configured. You can store these variables in a `project.env` file for easier management on Unix-like operating systems.

- **NOTIFY_TXT_PHONE_NUMBERS**: A comma-separated list of phone numbers to receive notifications.
- **TWILIO_ACCOUNT_SID**: Twilio API account SID, required to authenticate with Twilio.
- **TWILIO_AUTH_TOKEN**: Twilio API authentication token.
- **TWILIO_PHONE_NUMBER**: The Twilio phone number used as the sender for outgoing messages.

Run the following command to load the environment variables from `project.env` into your shell session:

```sh
source project.env
```

Once the environment variables are set, start the server with the `flask` command. Replace `SERVER_IP_ADDRESS` with your server's IP address.

```sh
flask --app server run --no-debug -h SERVER_IP_ADDRESS -p 5000 --cert ssl/server.crt --key ssl/server.key
```

## Start the Camera
Open the camera web application on a device like a smartphone or any computer with a web browser with a camera:

Open a web browser (tested with Google Chrome and Firefox) and navigate to:
https://SERVER_IP_ADDRESS/static/camera.html

If using a self-signed certificate, proceed through the security warning. Using HTTPS is necessary for the camera web application to gain access to the device's camera.

Now the device will automatically send camera photos regularly to the server. Check to make sure this is working by checking the camera image displayed and the log.