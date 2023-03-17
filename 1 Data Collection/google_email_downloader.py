# login to gmail account and download emails from inbox

import imaplib
import email

user = 'username'
# create an app password via https://myaccount.google.com/apppasswords
password = 'password'

imap_url = 'imap.gmail.com'
mail = imaplib.IMAP4_SSL(imap_url)
mail.login(user, password)

mail.select('inbox')
status, messages = mail.search(None, 'ALL')

count = 0

for num in messages[0].split():
    status, data = mail.fetch(num, '(RFC822)')
    
    for response_part in data:
        if type(response_part) is tuple:
            with open((str(count) + '.txt'), 'wb') as binary_file:
                binary_file.write(response_part[1])
            count+=1

mail.close()
mail.logout()