def parse_raw_email_header(__header_content: str) -> dict:
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
    value = ""
    for line in __header_content:
        if ":" in line:
            if key != "" and value != "":
                __header_dict[key] = value.strip()
                key = ""
                value = ""
            key, value = line.split(":", 1)
            key = key.strip()
            # check if the key is already in the dictionary, if it is, convert to list and append
            if key in __header_dict:
                if type(__header_dict[key]) == list:
                    __header_dict[key].append(value.strip())
                else:
                    __header_dict[key] = [__header_dict[key], value.strip()]
            else: # if it's not in the dictionary, add it
                __header_dict[key] = value.strip()

        else: # if the line does not contain a colon, it's probably a continuation of the previous value
            value += line.strip()

        # if we got the Content-Length header, we can break out of the loop because the rest is in html
        if key == "Content-Length" or key == "Content-length":
            break

    # add the html content to the dictionary; take the content after the first empty line (seems to be the standard with
    # htmls after that)
    __header_dict["html"] = "\n".join(__header_content[__header_content.index("") + 1:])

    return __header_dict