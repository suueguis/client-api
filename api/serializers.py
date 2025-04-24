from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Client
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        # Add user to 'USER' group by default
        user_group, created = Group.objects.get_or_create(name='USER')
        user.groups.add(user_group)
        
        return user

class ClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True)
    
    class Meta:
        model = Client
        fields = ('id', 'username', 'name', 'email', 'phone', 'address', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        user_data = self.context['request'].user
        client = Client.objects.create(
            user=user_data,
            name=validated_data['name'],
            email=validated_data['email'],
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        return client