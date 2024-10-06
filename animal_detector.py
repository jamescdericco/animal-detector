import argparse
from fastai.vision.all import *

def load_animal_detector_learner():
    script_dir = Path(__file__).parent
    model_path = script_dir / 'model' / 'export.pkl'
    return load_learner(model_path)

def main():
    parser = argparse.ArgumentParser(description="Classify the animal in a given food house camera photo")
    parser.add_argument('files', nargs='+', help='Paths to the image files')
    args = parser.parse_args()

    learn = load_animal_detector_learner()

    for file in args.files:
        img = PILImage.create(file)

        prediction, prediction_index, probabilities = learn.predict(img)
        print(f'File: {file}; Prediction: {prediction}; Probability: {probabilities[prediction_index]}')


if __name__ == '__main__':
    main()