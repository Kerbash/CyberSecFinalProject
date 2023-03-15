import threading
import queue
from time import sleep

from model.main import run
import tkinter as tk

# Test Login info "highlordofspam" "sqyupgeoyymxrcxj"

class GUI:
    # login to Gmail account and get emails from inbox
    def __init__(self):
        # create the main window
        self.window = tk.Tk()
        self.window.title('Spam Detector')

        self.canvas = tk.Canvas(self.window, width=600, height=300)
        self.canvas.grid(columnspan=2, rowspan=2)

        self.current_element = []

    def clear_page(self):
        for element in self.current_element:
            element.destroy()
        self.current_element = []

    def loading_page(self, username, password):
        # clear the window
        self.clear_page()

        # create a queue to store the result
        result = queue.Queue()

        # launch the run in a seperate thread
        self.thread = threading.Thread(target=run, args=(username, password, result))
        self.thread.start()

        # while the thread is running, update the canvas
        n_dot = 0
        self.current_element.append(tk.Label(self.window, text='Processing'))
        # add the label to the window center
        self.current_element[0].grid(row=0, column=0, columnspan=2)
        self.current_element[0].config(font=('Zalgo', 24, 'bold'))
        while self.thread.is_alive():
            # change the text to add a dot
            self.current_element[0].config(text='Processing' + '.' * n_dot)
            self.canvas.update()
            n_dot += 1
            n_dot %= 4
            sleep(0.5)

        # get the result from the thread
        self.thread.join()
        prediction = result.get()

        self.result_page(prediction)

    def result_page(self, prediction):
        # clear the window
        self.clear_page()

        # Create a frame for the scroll bar
        frame = tk.Frame(self.window)
        frame.grid(row=1, column=2, sticky="ns")

        # Create a listbox
        tk.Label(self.window, text='Spam Emails:').grid(row=0, column=0)
        listbox = tk.Listbox(self.window, width=100)
        listbox.grid(row=1, column=0, sticky="nsew")

        # fill listbox with spam emails
        for spam in prediction[0]:
            listbox.insert('end', 'From:' + spam['From'] + '; Subject:' + spam['Subject'])

        # Create a scroll bar
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")


        self.window.update()

    def detect_email(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.loading_page(username, password)

    def main_page(self):
        # create the username label and entry widget
        username_label = tk.Label(self.window, text='Username:')
        username_label.grid(row=0, column=0)
        self.current_element.append(username_label)

        self.username_entry = tk.Entry(self.window)
        self.username_entry.grid(row=0, column=1)
        self.username_entry.insert(0, 'highlordofspam')
        self.current_element.append(self.username_entry)

        # create the password label and entry widget
        password_label = tk.Label(self.window, text='Password:')
        password_label.grid(row=1, column=0)
        self.current_element.append(password_label)

        # fill the input with a default password "highlordofspam"
        self.password_entry = tk.Entry(self.window, show='*')
        self.password_entry.insert(0, 'sqyupgeoyymxrcxj')
        self.password_entry.grid(row=1, column=1)
        self.current_element.append(self.password_entry)

        # create the login button
        button_text = tk.StringVar()
        login_button = tk.Button(self.window, textvariable=button_text, command=self.detect_email)
        button_text.set('Login to Gmail')
        login_button.grid(row=2, column=0, columnspan=2)
        self.current_element.append(login_button)

    def run(self):
        # start the main event loop
        self.main_page()
        self.window.mainloop()

if __name__ == '__main__':
    gui = GUI()
    gui.run()