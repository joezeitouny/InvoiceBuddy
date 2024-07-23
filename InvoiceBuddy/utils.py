from datetime import datetime
import os
import shutil

from InvoiceBuddy import globals


def get_application_version():
    return globals.APPLICATION_VERSION


def get_application_name():
    return globals.APPLICATION_NAME


def try_parse_bool(value) -> bool:
    if not value:
        return False

    result = False
    try:
        if str(value).upper() == 'TRUE':
            result = True
    except Exception:
        pass

    return result


def try_parse_int(value) -> int:
    if not value:
        return 0

    result = 0
    try:
        result = int(value)
    except ValueError:
        pass
    return result


def try_parse_float(value) -> float:
    if not value:
        return 0.0

    result = 0.0
    try:
        result = float(value)
    except ValueError:
        pass
    return result


def are_values_close(value1, value2, tolerance):
    absolute_difference = abs(value1 - value2)
    return absolute_difference <= tolerance


def get_formatted_timestamp(value: int, is_in_milliseconds):
    if is_in_milliseconds:
        timestamp = value / 1000
    else:
        timestamp = value

    # Convert timestamp to datetime in UTC timezone
    utc_datetime = datetime.utcfromtimestamp(timestamp)

    # Format the datetime object to a readable date string in UTC timezone
    return utc_datetime.strftime('%Y-%m-%d %H:%M:%S') + ' UTC'


def find_nearest_timestamp(array_of_timestamps, target_timestamp):
    # Convert the target timestamp value to a datetime object
    target_datetime = datetime.utcfromtimestamp(target_timestamp)

    # Calculate the absolute difference between each timestamp in the array and the target timestamp
    differences = [abs(datetime.utcfromtimestamp(ts) - target_datetime) for ts in array_of_timestamps]

    # Find the index of the timestamp with the smallest absolute difference
    nearest_index = differences.index(min(differences))

    # Get the nearest timestamp from the array
    nearest_timestamp = array_of_timestamps[nearest_index]

    return nearest_timestamp


def check_file_exists(file_path):
    return os.path.exists(file_path)


def copy_file(src, dst):
    return shutil.copyfile(src, dst)
