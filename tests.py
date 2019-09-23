from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from django.urls.base import reverse

from .models import Event, UserProfile


class TestEvent(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        user_data = {"first_name": "Test",
                      "last_name": "Test",
                      "email": "user@example.com",
                      "password": "qwe12345"
                }
        # register user
        response = self.client.post(reverse("users"), user_data, format="json")
        self.user = UserProfile.objects.get()
        auth_data = {"username": "user@example.com",
                      "password": "qwe12345"}
        # jwt auth user
        response = self.client.post(reverse("auth"), auth_data, format="json")
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + response.data["token"])
    
     
    def test_get_events(self):
        response = self.client.get(reverse("events"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
     
    def test_create_event(self):
        event_data = {"name": "Test event",
                      "description": "Test event description",
                      "tags": [{"name": "tag1"}, {"name": "tag2"}]
            }
        response = self.client.post(reverse("events"), event_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().name, "Test event")
        self.event = Event.objects.get()
    
    
    def test_get_event(self):
        self.test_create_event()
        response = self.client.get(reverse("events", kwargs={"pk": self.event.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    def test_put_event(self):
        self.test_create_event()
        event_data = {"name": "Test event 2",
                      "description": "Test event description 2",
                      "tags": [{"name": "tag1"}, {"name": "tag3"}]
            }
        response = self.client.put(reverse("events", kwargs={"pk": self.event.id}), event_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.event.id)
        self.assertEqual(response.data["name"], "Test event 2")
