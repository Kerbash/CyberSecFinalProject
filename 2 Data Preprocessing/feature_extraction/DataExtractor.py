from bs4 import BeautifulSoup


def get_tld(s: str) -> str:
    """
    Get the Top Level Domain from the organization string
    unfortunately, this is not a perfect solution as sometimes there may be multiple . like parliament.gov.uk
    :param s: the organization string
    :return: the TLD
    """
    output = s.split(".")[-1]
    # trim any non-alphanumeric characters from the end of the string
    while not output[-1].isalnum():
        output = output[:-1]
    return output


def get_server_ip(s: str) -> str:
    """
    Get the server ip from the received string
    :param s: the received string
    :return: the server ip
    """
    # get


def get_type(s: str) -> str:
    """
    Get the type of the content
    :param s:  type string
    :return: the type of the content
    """
    return s.split(";")[0]


def get_body_text(s: str) -> str:
    """
    Get the text body of the email
    :param s: the html body of the email
    :return: the text body of the email
    """
    s = BeautifulSoup(s, "html.parser")
    return s.get_text().replace("\n", " ")


def extract_interesting_data(header: dict, extract: list = None) -> dict:
    """
    Extact all the interesting data from a raw txt email header
    :param extract: list of string to extract (must be in interesting_data)
    :param header: the parsed header of the email
    :return: the interesting data in dictionary form
    """
    # list of interesting data to extract
    # the first item is the key to be stored as
    # the value pair are first the key in the header dictionary and then the function to be applied to the value
    interesting_data = {
        "date": ["Date", None],
        "tld": ["From", get_tld],
        "subject": ["Subject", None],
        "content_length": ["Content-Length", None],
        "content_type": ["Content-Type", get_type],
        "precedence": ["Precedence", None],
        "html": ["html", get_body_text],
        "List-Unsubscribe": ["List-Unsubscribe", None]
    }
    output = {}
    if extract is None:
        extract = interesting_data.keys()

    for key in extract:
        if key not in interesting_data.keys():
            raise ValueError(f"Key {key} not in interesting_data")
        temp = interesting_data[key]
        if temp[1] is None:
            try:
                output[key] = header[temp[0]]
            except KeyError:
                output[key] = None
        else:
            try:
                output[key] = temp[1](header[temp[0]])
            except KeyError:
                output[key] = None

    return output
