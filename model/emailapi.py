import imaplib
import os


class EmailHeaderPuller:
    def __init__(self, user, password, imap_url='imap.gmail.com'):
        self.user = user
        self.password = password
        self.imap_url = imap_url

    def pull_headers(self, folder='inbox', limit=100):
        # clear the temp folder
        for file in os.listdir("temp"):
            os.remove(os.path.join("temp", file))

        # create an app password via https://myaccount.google.com/apppasswords
        mail = imaplib.IMAP4_SSL(self.imap_url)
        mail.login(self.user, self.password)

        # select the folder
        mail.select(folder)
        status, messages = mail.search(None, f'1:{limit}')

        count = 0

        # for each message
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')

            for response_part in data:
                if type(response_part) is tuple:
                    with open(f"temp/{str(count)}.txt", 'wb') as binary_file:
                        binary_file.write(response_part[1])
                    count += 1

        mail.close()
        mail.logout()