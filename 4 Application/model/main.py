import queue
import os

from .emailapi import EmailHeaderPuller
from .email_processor import parse_email
from .model import load_model


def run(username, password, result : queue.Queue, folder="inbox", limit=10):
    # check if a temp folder exists if not create one
    if not os.path.exists("temp"):
        os.mkdir("temp")

    # call the email puller
    email_puller = EmailHeaderPuller(username, password)
    email_puller.pull_headers(folder, limit)
    # the email headers are now in the temp folder

    # call the email parser
    df, email, error = parse_email("temp\\")

    # load the model
    model = load_model()
    prediction = model.predict(df)

    # clear temp folder
    for file in os.listdir("temp"):
        os.remove("temp\\" + file)


    # clear last result
    result.queue.clear()
    # break the prediction into a list of spam and ham
    spam = []
    ham = []
    for i in range(len(prediction)):
        if prediction[i] == 1:
            # get the email at index i
            spam.append(email.iloc[i])
        else:
            ham.append(email.iloc[i])

    prediction = [spam, ham]

    result.put(prediction)
