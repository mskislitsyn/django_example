import os

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from users.models import UserProfile, Event, Tag, Category
from users.api.v1.serializer import TempFileSerializer, UserProfileSerializer, EventSerializer, EventFileSerializer, TagSerializer, CategorySerializer


class TempFile(APIView):
    """
    Api point for load event's files when event not create 
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        serializer = TempFileSerializer(data=request.FILES)
        if serializer.is_valid():
            save_file = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'server_file_name': os.path.basename(save_file.name)}, status=status.HTTP_201_CREATED)
    

class UserPhotoView(APIView):
    """
    API point for loading user photo
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)
  
    def post(self, request, *args, **kwargs):
        try:
            photo = request.FILES.get('photo', None)
            if photo:
                request.user.photo = photo
                request.user.save()
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
    
        return Response(status=status.HTTP_201_CREATED)

class EventFileView(APIView):
    """
    API point for loading files for existing event 
    """
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file', None)
            if file:
                data = {'file': file, 
                        'name': file.name, 
                        'event': request.data['event']}
                serializer = EventFileSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
                return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class TagList(generics.ListCreateAPIView):
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by('-name')
    permission_classes = (IsAuthenticatedOrReadOnly,)


class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('-name')
    permission_classes = (IsAuthenticatedOrReadOnly,)


class UserProfileList(generics.ListCreateAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all().order_by('-id')


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)


class EventList(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    
    def get_serializer_class(self):
        return generics.ListCreateAPIView.get_serializer_class(self)
    
    def get_queryset(self):
        category = self.request.query_params.get('category', None)
        queryset = Event.objects.all().order_by('-id')
        if category:
            queryset = queryset.filter(category__pk=category)
        return queryset
    
 
class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
