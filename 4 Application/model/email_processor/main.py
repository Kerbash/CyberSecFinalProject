import json
import os

import pandas as pd
from datetime import datetime

from .DataExtractor import extract_interesting_data
from .Normalizer import quantify_normalize

FEATURES_TO_EXTRACT = ["precedence", "subject_punctuation_punctuation_count", "subject_symbol_money_sign_count",
                        "subject_misspelled", "subject_capital_letters", "subject_word_count", "subject_sentence_count",
                        "capital_letters", "word_count", "sentence_count", "exclamation", "email_count",
                        "message_punctuation_punctuation_count", "message_symbol_symbol_word_count",
                        "message_symbol_large_sum_count", "message_misspelled", "message_wfreq_0", "message_wfreq_32",
                        "message_wfreq_244", "message_wfreq_2", "message_wfreq_31", "message_wfreq_45", "message_wfreq_1",
                        "message_wfreq_1148", "message_wfreq_152", "message_wfreq_51", "message_wfreq_27", "message_wfreq_23",
                        "message_wfreq_108", "message_wfreq_111", "message_wfreq_165", "message_wfreq_157", "message_wfreq_16",
                        "message_wfreq_33", "message_wfreq_59", "message_wfreq_349", "message_wfreq_110", "message_wfreq_117",
                        "message_wfreq_116", "message_wfreq_4", "message_wfreq_122", "message_wfreq_68", "message_wfreq_57",
                        "message_wfreq_362", "message_wfreq_2083", "message_wfreq_249", "message_wfreq_24", "message_wfreq_37",
                        "message_wfreq_65", "subject_wfreq_59", "message_wfreq_1150", "message_wfreq_289", "message_wfreq_81",
                        "tld_co", "tld_com", "tld_jp", "tld_net", "tld_org", "tld_us", "tld_xyz"]


def parse_email_header(__header_content: str) -> dict:
    """
    Parse the string header of an email into a dictionary
    :param __header_content: the string header of an email
    :return: the dictionary of the email
    """
    __header_content = __header_content.strip().split("\n")
    __header_dict = {}
    # to handle multi-line header values the list is broken into a list of lines, if the line contains a colon,
    # we know that it's probably a value pair if it does not its probably a continuation of the previous value
    key = ""
    for line in __header_content:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            __header_dict[key] = value.strip()
        else:
            __header_dict[key] += line.strip()

        # if we got the Content-Length header, we can break out of the loop because the rest is in html
        if key == "Content-Length" or key == "Content-length":
            break

    # add the html content to the dictionary; take the content after the first empty line (seems to be the standard with
    # htmls after that)
    __header_dict["html"] = "\n".join(__header_content[__header_content.index("") + 1:])

    return __header_dict


def parse_email(path):
    # get all files in the temp folder
    files = os.listdir(path)
    error = 0
    df = pd.DataFrame()
    parsed_df = pd.DataFrame()
    # clear the folder

    for file in files:
        with open(path + file) as f:
            try:
                email_text = f.read()
                parsed = parse_email_header(email_text)

                # concat the parsed email to a parsed dataframe at index number datatype
                parsed_df = pd.concat([parsed_df, pd.DataFrame(parsed, index=[file], columns=["From", "Subject", "Received"])], ignore_index=True)

                header_dict = extract_interesting_data(parsed)
                header_dict = quantify_normalize(header_dict)
                # extract the FEATURES_TO_EXTRACT if exist in header_dict
                temp = pd.DataFrame()
                for feature in FEATURES_TO_EXTRACT:
                    try:
                        temp[feature] = [header_dict[feature]]
                    except KeyError:
                        temp[feature] = [0]

                # save the header_dict to a json file
                with open(path + file + ".json", "w") as json_file:
                    json.dump(header_dict, json_file)

                # set all NaN and None to 0
                temp = temp.fillna(0)
                # add it to index i
                df = pd.concat([df, temp], ignore_index=True)

            except Exception as e:  # if something went wrong
                print("Error: ", e)
                f.close()
                error = error + 1
                # move to error

        # remove the original
        # os.remove(path + file)

    return df, parsed_df, error