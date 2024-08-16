from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User
from django.core import exceptions


class SignUpUserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
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


class LoginUserSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)
        token = serializers.CharField(read_only=True)

        def validate(self, data):
            email = data.get('email', '')
            password = data.get('password', '')
            # user = User.objects.filter(email__iexact=email).first()
            if not email and not password:
                raise serializers.ValidationError("Please provide both email and password")
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this email does not exist")
            
            if not user.check_password(password):
                raise serializers.ValidationError("Password is incorrect")
            
            
            user = authenticate(email=user.email, password=password)

            if not user:
                raise serializers.ValidationError("Authentication failed. Please check your email and password")

            token, _ = Token.objects.get_or_create(user=user)
            data['token'] = token.key
            data['user'] = user
            return data

        # def validate(self, data):
        #     email = data.get('email', '')
        #     password = data.get('password', '')

        #     user = User.objects.filter(email__iexact=email).first()

        #     if not user:
        #         raise serializers.ValidationError("Invalid email or password")

        #     if not user.check_password(password):
        #         raise serializers.ValidationError("Invalid email or password")

        #     user = authenticate(username=user.username, password=password)

        #     if not user:
        #         raise serializers.ValidationError("Authentication failed")

        #     token, _ = Token.objects.get_or_create(user=user)

        #     return {
        #         'token': token.key,
        #         'user_id': user.id,
        #         'email': user.email
        #     }