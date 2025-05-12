import datetime
import random
import string


def generate_unique_filename(extension='jpg'):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    unique_filename = f"{timestamp}_{random_string}.{extension}"
    return unique_filename
