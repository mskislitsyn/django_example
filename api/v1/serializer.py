from django.conf import settings
from django.core.files import File
from django.db.models.query import QuerySet

from rest_framework import serializers

from users.models import UserProfile, Event, EventFile, Tag, Category
from users.tools import get_temp_file_path, get_upload_temp_file_path, remove_temp_file, get_address


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserProfileSerializer(user, context={'request': request}).data
    }


class TempFileSerializer(serializers.Serializer):
    """
    For dynamic file loading
    """
    file = serializers.FileField()
    
    def create(self, validated_data):   
        file = validated_data.get('file')
        destination = get_upload_temp_file_path(file.name)

        with open(destination, 'wb+') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
        
        return temp_file
        

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = ['id', 
                  'last_name', 
                  'first_name', 
                  'email', 
                  'password', 
                  'last_login', 
                  'date_joined', 
                  'phone_number', 
                  'photo']
        extra_kwargs = {'password': {'write_only': True}}
     
    def validate_email(self, email):
        """
        Check that user with email not register
        """
        try:
            UserProfile.objects.get(email__iexact=email)
        except UserProfile.DoesNotExist:
            return email
        
        raise serializers.ValidationError("A user with that email address already exists.")
    
    def create(self, validated_data): 
        user = super(UserProfileSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 
                  'name', 
                  'code']


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ['id',
                  'name']


class EventFileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EventFile
        fields= ['id',
                 'file', 
                 'name',
                 'event']
        extra_kwargs = {'event': {'write_only': True}}
    
    def create(self, validated_data):
        return serializers.ModelSerializer.create(self, validated_data)
        

class EventSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(read_only=True, source="host.get_full_name")
    host_photo = serializers.FileField(read_only=True, source="host.photo")
    category_name = serializers.CharField(read_only=True, source="category.name")
    files = EventFileSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)
    
    class Meta:
        model = Event
        fields = ['id', 
                  'name', 
                  'description', 
                  'files', 
                  'tags', 
                  'host', 
                  'host_name', 
                  'host_photo', 
                  'created', 
                  'category',
                  'category_name', 
                  'latitude', 
                  'longitude', 
                  'address']
    
    def validate(self, validated_data):
        # when event create files have special temp name 'server_file_name' for file and get current user from request
        if self.context['request'].method == 'POST':
            validated_data['files'] = self.context['request'].data.get('files', [])
            validated_data['host'] = self.context['request'].user
        return serializers.ModelSerializer.validate(self, validated_data)
    
    def create(self, validated_data):
        files = validated_data.pop('files', [])
        tags = validated_data.pop('tags', [])
        event = Event.objects.create(**validated_data)
        
        # try to geocode address and save address in Event
        if event.latitude and event.longitude:
            try:
                event.address = get_address(event.latitude, event.longitude)
                event.save()
            except:
                pass
        
        # save event's tags
        for tag in tags:
            tag, created = Tag.objects.get_or_create(name=tag['name'])
            event.tags.add(tag)
            
        # save event's files from temp folder
        for file in files:
            temp_file_dir = get_temp_file_path(file['server_file_name'])
            with open (temp_file_dir, 'rb') as event_file:
                name = file['name']
                event_file = File(event_file)
                event_file.name = name
                EventFile.objects.create(file=event_file, name=name, event=event)
            remove_temp_file(temp_file_dir)

        return event
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.date_start = validated_data.get('date_start', instance.date_start)
        instance.date_end = validated_data.get('date_end', instance.date_end)
        
        # set new address if coords changed
        if instance.latitude != validated_data.get('latitude', instance.latitude) or instance.longitude != validated_data.get('longitude', instance.longitude):
            instance.latitude = validated_data.get('latitude', instance.latitude)
            instance.longitude = validated_data.get('longitude', instance.longitude)
            try:
                instance.address = get_address(instance.latitude, instance.longitude)
            except:
                pass
            
        instance.save()
        
        # update tags in event
        exist_tags = instance.tags.all()
        keep_tags = []
        for tag in tags:
            tag, created = Tag.objects.get_or_create(name=tag['name'])
            keep_tags.append(tag.id)
            if tag in exist_tags:
                continue
            else:
                instance.tags.add(tag)
        
        exist_tags.exclude(id__in=keep_tags).delete()
        
        return instance
