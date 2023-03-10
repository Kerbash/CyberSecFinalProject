from .emailapi import EmailHeaderPuller
from .email_processor import parse_email
from .model import load_model


def run(username, password, folder="inbox", limit=10):
    # call the email puller
    email_puller = EmailHeaderPuller(username, password)
    email_puller.pull_headers(folder, limit)
    # the email headers are now in the temp folder

    # call the email parser
    df, error = parse_email("temp\\")

    # load the model
    model = load_model()
    prediction = model.predict(df)
    print(prediction)
