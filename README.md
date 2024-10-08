# Setup Server
The server requires a Linux operating system (this project was tested on Ubuntu 24.04 with the x86_64 architecture). Even though the server uses a deep neural network model to do image classification, it does not use the GPU, as PyTorch is configured to run CPU-only for inference in `environment.yml`.

Install [miniconda](https://docs.anaconda.com/miniconda/)

Create the `animal_detector` environment, including Python and this project's dependencies.
```sh
conda env create -f environment.yml
```

# Setup the Image Classification Model

Download the PyTorch model from https://www.kaggle.com/models/jamesdericco/animal_detector_model/. Save this file as `export.pkl` in a `model` subdirectory of the project root.

This model was generated in the Kaggle notebook https://www.kaggle.com/code/jamesdericco/animal-detector. The data used to train the model is available at https://www.kaggle.com/datasets/jamesdericco/cat-food-cam-20241006/.

# Run Server
First export all of the required environment variables for configuration.

```sh
source project.env
```

Launch the server with the flask command (fill in SERVER_IP_ADDRESS):
```sh
flask --app server run --no-debug -h SERVER_IP_ADDRESS -p 5000 --cert ssl/server.crt --key ssl/server.key
```

# Start the Camera
Open the camera web application on a device like a smartphone or any computer with a web browser with a camera:

Open a web browser (tested with Google Chrome and Firefox) and navigate to:
https://SERVER_IP_ADDRESS/static/camera.html

If using a self-signed certificate, proceed through the security warning. Using HTTPS is necessary for the camera web application to gain access to the device's camera.

Now the device will automatically send camera photos regularly to the server. Check to make sure this is working by checking the camera image displayed and the log.