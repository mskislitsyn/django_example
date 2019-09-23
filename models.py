
from django.db import models
from django.contrib.auth.models import AbstractUser

from .tools import get_user_photo_upload_path, get_event_file_upload_path
from django.utils import timezone



class UserProfile(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    photo = models.FileField(upload_to=get_user_photo_upload_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        username = self.email
        self.username = username
        super(UserProfile, self).save(*args, **kwargs)
    
    def get_location_history(self):
        return self.location_history


class UserLocationHistory(models.Model):
    user = models.ForeignKey(UserProfile, blank=True, null=True, default=None, on_delete=models.CASCADE, related_name="location_history")
    country_code = models.CharField(max_length=3, blank=True, null=True)
    country_name = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    ip = models.GenericIPAddressField()


class Tag(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=30)
    
    def __str__(self):
        return self.code

    
class Event(models.Model):
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, related_name='events')
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=1000, null=True)
    host = models.ForeignKey(UserProfile, blank=True, null=True, on_delete=models.SET_NULL, related_name='events')
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    tags = models.ManyToManyField(Tag)
    
    def __str__(self):
        return self.name
    
    def get_files(self):
        return self.files


class EventFile(models.Model):
    file = models.FileField(upload_to=get_event_file_upload_path, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    upload_time = models.DateTimeField(auto_now=True, blank=True, null=True)
    event = models.ForeignKey(Event, related_name='files', blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.name
    