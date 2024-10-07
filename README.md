# Setup
Install [miniconda](https://docs.anaconda.com/miniconda/)

Create the `animal_detector` environment, including Python and this project's dependencies.
```sh
conda env create -f environment.yml
```

# Run Server
First export all of the required environment variables for configuration.

```sh
source project.env
```

Launch the server with the flask command (fill in YOUR_IP_ADDRESS):
```sh
flask --app server run --no-debug -h YOUR_IP_ADDRESS -p 5000 --cert ssl/server.crt --key ssl/server.key
```
