from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from .models import User
from django.core import exceptions


class SignUpUserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
    # phone = serializers.CharField(write_only=True, max_length=20)
    # password = serializers.CharField(write_only=True, validators=[password_validation.validate_password])
    confirm_password = serializers.CharField(write_only=True, max_length=50)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'phone',
            'password',
            'confirm_password',
            'email',
            'is_verified',
            'date_joined',
            'token',
            
        ]
        read_only_fields = ['id', 'token', 'date_joined', 'is_verified']

        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'confirm_password': {'write_only': True, 'required': True},
        }


    def validate(self, data):
        error = {}    
        confirm_password = data.get('confirm_password', '')
        password = data.get('password', '')
        email = data.get('email', '')

        if password.lower() != confirm_password.lower():
            error['confirm_password'] = ['Passwords do not match']
        try:
            validate_password(password=password) and validate_password(password=confirm_password)

        except exceptions.ValidationError as e:
            error['password'] = list(e.messages)        


        email_ = User.objects.filter(email__iexact=email)
        if email_.exists():
            error['email'] = ['Email already exists']

        # if User.objects.filter(username=username).exists():
        #    raise ValidationError("Username already exists")
    


        if error:
            raise serializers.ValidationError(error)
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        self.token = token.key
        return user
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(self, "token"):
            data['token'] = self.token
        return data



