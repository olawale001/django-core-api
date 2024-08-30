import email
from rest_framework import serializers, generics
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User, ForgetPassword
from django.core import exceptions
from utils.utility import send_otp
from django.shortcuts import get_object_or_404
from django.utils import timezone



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
        send_otp(user, validated_data.get('email'), 'Email verification' )
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


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email', '')
        otp = data.get('otp', '')

        user = get_object_or_404(User, email__iexact=email)
        try:
            forget_password = get_object_or_404(ForgetPassword, user=user, otp=otp)
        except ForgetPassword.DoesNotExist:
            raise serializers.ValidationError({"otp":"Invalid OTP or otp does not exist"})
        
        if timezone.now() > forget_password.created_at  + timezone.timedelta(minutes=15):
            raise serializers.ValidationError({"OTP": "otp is expired"})
        
        return data
        


    def save(self,  **kwargs):
        email = self.validated_data.get('email')
        user = get_object_or_404(User, email__iexact=email)

        if not  user.is_verified:
            user.is_verified = True
            user.save()
            return user
        
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)     

    def validate_email(self, data):
        if not User.objects.filter(email__iexact=data).exists():
            raise serializers.ValidationError("Email does not exist")
        return data
    
    def save(self, **kwargs):
        email = self.validated_data['email']
        user = get_object_or_404(User, email__iexact=email)
        send_otp(user, email, "Reset Password")
        return user
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)


    def validate(self, data):
        email = data.get('email', '')
        otp = data.get('otp', '')
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        if password !=  confirm_password:
            raise serializers.ValidationError({"password": "Password and confirm password does not match"})
        user  = get_object_or_404(User, email__iexact=email)
        forget_password = get_object_or_404(ForgetPassword, user=user, otp=otp)

        if timezone.now()  > forget_password.created_at  + timezone.timedelta(minutes=15):
            raise serializers.ValidationError({"OTP": "otp is expired"})
        try:
            validate_password(password)
        except exceptions.ValidationErrornas as e:
          raise serializers.ValidationError({"password": e.message})

        return data
    
    def save(self):
        email = self.validated_data['email']
        password = self.validated_data['password']
        user = get_object_or_404(User, email__iexact=email)
        user.set_password(password)
        user.save()
        return user