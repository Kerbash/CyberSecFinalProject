import os

from joblib import load, dump

# get the location of the current file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH = "model\\"
FILE_NAME = 'modelv1.joblib'


class Model:
    def __init__(self, model):
        self.model = model

    def predict(self, input_data):
        return self.model.predict(input_data)

    def score(self, input_data, output_data):
        return self.model.score(input_data, output_data)


def load_model():
    # Load the model
    loaded_model = load(CURRENT_DIR + "\\" + FILE_NAME)
    return Model(loaded_model)


def save_model(model):
    dump(model, CURRENT_DIR + "\\" + FILE_NAME)
