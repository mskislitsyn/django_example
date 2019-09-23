import uuid
import os

from django.conf import settings

from geopy.geocoders import Nominatim


def generate_temp_file_name(filename):
    return "{0}_{1}".format(uuid.uuid4(), filename)


def get_temp_file_path(filename):
    return os.path.join(settings.TEMP_ROOT, filename)


def get_upload_temp_file_path(filename):
    filename = generate_temp_file_name(filename)
    return get_temp_file_path(filename)


def remove_temp_file(file_dir):
    os.remove(file_dir)


def get_user_photo_upload_path(instance, filename):
    return os.path.join("users/", str(instance.id),  os.path.basename(filename))


def get_event_file_upload_path(instance, filename):
    return os.path.join("events/", str(instance.event.id),  os.path.basename(filename))


def get_address(latitude, longitude):  
    geolocator = Nominatim()
    coords = latitude, longitude
    location = geolocator.reverse(coords)
    address = location.address
    return address
