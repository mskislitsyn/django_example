from django.urls import path
from users.api.v1 import views

urlpatterns = [
    path('userphoto/', views.UserPhotoView.as_view()),
    path('eventfiles/', views.EventFileView.as_view()),
    path('uploadfile/', views.TempFile.as_view()),
    path('tags/', views.TagList.as_view(), name='tags'),
    path('categories/', views.CategoryList.as_view(), name='categories'),
    path('users/', views.UserProfileList.as_view(), name='users'),
    path('users/<pk>/', views.UserProfileDetail.as_view(), name='users'),
    path('events/', views.EventList.as_view(), name='events'),
    path('events/<pk>/', views.EventDetail.as_view(), name='events'),
]