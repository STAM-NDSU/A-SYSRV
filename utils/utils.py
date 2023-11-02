import datetime
import hashlib

def get_current_datetime():
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    return timestamp

def get_current_datetime_hash():
    md5_hash = hashlib.md5()
    md5_hash.update(get_current_datetime().encode('utf-8'))
    md5_hex = md5_hash.hexdigest()
    return md5_hex