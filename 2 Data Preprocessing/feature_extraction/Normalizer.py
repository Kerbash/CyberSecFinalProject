from datetime import datetime
from pprint import pformat
from bs4 import BeautifulSoup
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import words as ntlkwords

from .wordslib import known_words
import re

first_time_wordnet = True
# list of english words
english_words = []


def precedence_to_int(name: str, precedence: str) -> dict:
    """
    Convert the precedence string to an integer
    :param name: key name
    :param precedence: precedence in the email header
    :return: the int of the precedence
    """
    # Fix and clean up precedence column
    if precedence in ['bulk', 'list', 'junk', 'Bulk']:
        return {name: 1}
    else:
        return {name: 0}


def to_epoch(name: str, input: str) -> dict:
    """
    Convert a date string to epoch time
    :param input: the date string
    :param name: name of the key
    :return: the epoch time
    """

    date_list = re.split(r'[:,\s]+', input)
    # pop all front elements that are not numbers
    while not date_list[0].isdigit():
        date_list.pop(0)
    # pop all back elements that are not numbers
    while not date_list[-1].isdigit():
        date_list.pop()
    # convert the elements at index 1 from month to number
    date_list[1] = datetime.strptime(date_list[1], "%b").month

    # load it into a datetime object
    date = datetime(day=int(date_list[0]),
                    month=int(date_list[1]),
                    year=int(date_list[2]),
                    hour=int(date_list[3]),
                    minute=int(date_list[4]),
                    second=int(date_list[5]))
    # convert to epoch
    return {name: int(date.timestamp())}


def count_capital_letters(name: str, input: str) -> dict:
    """
    Count the number of capital letters in a string
    :param input: the string to be counted
    :param name: name of the key
    :return: the number of capital letters in the string
    """
    # count capital letters in s
    return {name: sum(1 for c in input if c.isupper())}


def count_words(name: str, input: str) -> dict:
    """
    Count the number of words in a string
    :param input: the string to be counted
    :param name: name of the key
    :return: the number of words in the string
    """
    return {name: len(input.split())}


def count_sentence(name: str, input: str) -> dict:
    """
    Count the number of sentences in a string
    :param input: the string to be counted
    :param name: name of the key
    :return: the number of sentences in the string
    """
    return {name: len(re.split(r'[.!?]', input))}


def get_exclamation(name: str, input: str) -> dict:
    """
    Get the number of exclamation marks in the string
    :param input:  to be counted
    :param name: name of the key
    :return: the number of exclamation marks in the string
    """
    return {name: input.count("!")}


def get_email_count(name: str, input: str) -> dict:
    """
    Count the number of emails in a string
    :param input: the string to be counted
    :param name: name of the key
    :return: the number of emails in the string
    """
    return {name: len(re.findall(r'[\w\.-]+@[\w\.-]+', input))}


"""=====================================================================================================================
WORD ANALYZER AND HELPER FUNCTIONS
====================================================================================================================="""


def word_analyzer(name: str, input: str) -> dict:
    """
    Analyze a string for misspelled words, words with symbols, and words with numbers
    :param input: the string to be analyzed
    :param name: name of the key in this case the prefix
    :return:
    """
    output = {}
    # break the string into words
    input = input.split()

    # count the punctuation and remove it from the word
    output.update(get_punctuation(name + "_punctuation", input))

    # count the number of words with random symbols and numbers and remove them from the list
    output.update(get_symbol_words(name + "_symbol", input))
    # remove empty strings from the list
    input = [word for word in input if word.strip() != ""]

    # count the number of misspelled words
    output.update(get_misspelled(name + "_misspelled", input))
    # remove empty strings from the list
    input = [word for word in input if word.strip() != ""]

    # lemmatize the words
    lemmatize(input)
    # count the frequency of the words
    output.update(word_frequency(name, input))
    output.update(mapper(name, output[name + "_word_freq"]))
    # delete message word freq
    del output[name + "_word_freq"]

    return output


def mapper(name: str, input: list) -> dict:
    """
    Map the words freq list to a numerical value for each word
    :param name: name of the key
    :param input: the list of words to be mapped
    :return: the mapped dictionary
    """
    output = {}
    # iterate each of the frequency
    for word in input:
        # look up the word in the known words dictionary
        if word not in known_words:
            known_words[word] = len(known_words)

        # add the word to the output dictionary as a numerical value
        output[name + "_wfreq_" + str(known_words[word])] = input[word]

    # save the known_words dictionary to the wordslib file
    with open("wordslib.py", "w") as f:
        # write in pretty print format
        f.write("known_words = " + pformat(known_words))

    return output


def word_frequency(name: str, input: list) -> dict:
    """
    Count the frequency of the words in a string
    :param name: prefix of the key
    :param input: the list of words to be counted
    :return: the frequency of the words in the string
    """
    # Tokenize the text into words
    fd = nltk.FreqDist(input)
    return {name + "_word_freq": fd}


def lemmatize(input: list):
    """
    Lemmatize the words in a string
    :param input: the string to be lemmatized
    :return: the lemmatized string
    """
    global first_time_wordnet
    # download wordnet if it's the first time the function is called
    if first_time_wordnet:
        nltk.download('wordnet')
        # set first_time_launched to False so that the function is not called again
        first_time_wordnet = False

    # create a lemmatizer
    lemmatizer = WordNetLemmatizer()
    # lemmatize the words
    for word_index in range(len(input)):
        input[word_index] = lemmatizer.lemmatize(input[word_index]).lower()


def get_punctuation(name: str, input: list) -> dict:
    """
    Get the number of punctuation marks in the word list
    :param name: name of the key
    :param input: the list of words to be checked
    :return: the number of punctuation marks in the word list
    """
    with_punc = 0
    for word_index in range(len(input)):
        # check the front and back for the word for punctuation
        if input[word_index][0] in [".", ",", "!", "?", ";", ":", "(", ")", "[", "]", "{", "}", "'", '"']:
            # remove the punctuation
            with_punc += 1
            input[word_index] = input[word_index][1:]
        try:
            if input[word_index][-1] in [".", ",", "!", "?", ";", ":", "(", ")", "[", "]", "{", "}", "'", '"']:
                with_punc += 1
                input[word_index] = input[word_index][:-1]
        except IndexError:
            # only one character in the word
            pass

    return {name + "_punctuation_count": with_punc}


def get_symbol_words(name: str, input: list) -> dict:
    """
    Get the number of words with symbols and numbers in them and set them to empty strings
    :param name: the name of the key to be set as the prefix
    :param input: the list of words to be checked
    :return: a dictionary of XX_symbol_word_count and XX_money_sign_count
    """
    with_symbol = 0
    money_signs = 0
    large_sum = 0
    for word_index in range(len(input)):
        # check if the word has a symbol in it
        if not input[word_index].isalpha():
            # check for money signs
            if "$" in input[word_index] or "£" in input[word_index] or "€" in input[word_index]:
                money_signs += 1

            # check for numbers
            if any(char.isdigit() for char in input[word_index]):
                # first check if it's not a date
                if "/" not in input[word_index] or "-" not in input[word_index]:
                    # remove all characters that are not numbers
                    input[word_index] = ''.join([char for char in input[word_index] if char.isdigit()])
                    # convert to int
                    try:
                        input[word_index] = int(input[word_index])
                        # check if the number is a large sum
                        if input[word_index] > 3000:
                            large_sum += 1
                    except ValueError:
                        pass

            with_symbol += 1
            # set as empty string so that it is removed from the list
            input[word_index] = ""

    return {name + "_symbol_word_count": with_symbol,
            name + "_money_sign_count": money_signs,
            name + "_large_sum_count": large_sum}


def get_misspelled(name: str, input: list) -> dict:
    """
    Get the number of times a word is misspelled in a string
    :param input: the string to be checked
    :param word: the word to be checked
    :return: the number of times the word is misspelled
    """
    global first_time_wordnet
    global english_words
    if first_time_wordnet is True:
        nltk.download('words')
        english_words = ntlkwords.words()
        first_time_wordnet = False

    count = 0
    # count the number of times the word is misspelled and remove it from the list
    for word_index in range(len(input)):
        if input[word_index] not in english_words:
            count += 1
            input[word_index] = ""
    return {name: sum(1 for word in input if word not in english_words)}


def quantify_normalize(header: dict, extract: list = None) -> dict:
    """
    quantify and normalize the data
    :param header: the parsed header of the email after extracted
    :param extract: list of string to extract (must be in normalizable)
    """
    # list of interesting data to extract
    # the first item is key name
    # the value pair are first the key in the header dictionary and then the function to be applied to the value
    # NOTE: word_count, sentence_count, and capital_letters use a specialized temporary function which creates a new
    # var so that the soup function is not called multiple times
    normalizable = {
        "date": ["date", to_epoch],
        "tld": ["tld", None],
        "List-Unsubscribe": ["List-Unsubscribe", None],

        "precedence": ["precedence", precedence_to_int],

        "subject": ["subject", word_analyzer],
        "subject_capital_letters": ["subject", count_capital_letters],
        "subject_word_count": ["subject", count_words],
        "subject_sentence_count": ["subject", count_sentence],

        "capital_letters": ["raw_message", count_capital_letters],
        "word_count": ["raw_message", count_words],
        "sentence_count": ["raw_message", count_sentence],
        "exclamation": ["raw_message", get_exclamation],
        "email_count": ["raw_message", get_email_count],
        "message": ["raw_message", word_analyzer]
    }
    # create this new var so that the soup function is not called multiple times
    header["raw_message"] = BeautifulSoup(header["html"], "html.parser").get_text().replace("\n", " ")

    output = {}
    if extract is None:
        extract = normalizable.keys()

    for key in extract:
        if key not in normalizable.keys():
            raise ValueError(f"Key {key} not in normalizable list")
        temp = normalizable[key]

        if temp[1] is None:
            # if there is no post function then just add the value to the output
            output.update({key: header[temp[0]]})
        else:
            # run the post function and add the output to the output
            output.update(temp[1](key, header[temp[0]]))

    return output
