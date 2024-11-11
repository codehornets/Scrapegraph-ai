def remove_after_first_slash(input_string):
    i = 0
    str_len = len(input_string)
    while True:
        if i < str_len:
            char = input_string[i]
            if char == "/":
                if i + 1 < len(input_string) and input_string[i + 1] == "/":
                    i += 2
                    continue
                else:
                    return input_string[0:i]
            i += 1
        else:
            break
    return input_string


def get_filename_from_response_headers(response):
    content_disposition = response.headers.get("Content-Disposition")
    filename = content_disposition.split("filename=")[1].strip('"')
    return filename