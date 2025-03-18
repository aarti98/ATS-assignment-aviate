import re
from rest_framework import serializers
from .models import Candidate


class CandidateCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        error_messages={
            'invalid': 'Please enter a valid email address',
            'required': 'Email is required'
        }
    )
    gender = serializers.ChoiceField(
        choices=Candidate.GENDER_CHOICES,
        error_messages={
            'invalid_choice': 'Gender must be one of: M (Male), F (Female), O (Other)',
            'required': 'Gender is required'
        }
    )
    age = serializers.IntegerField(
        min_value=18,
        max_value=100,
        error_messages={
            'min_value': 'Age must be at least 18',
            'max_value': 'Age cannot be more than 100',
            'required': 'Age is required',
            'invalid': 'Age must be a valid integer'
        }
    )
    phone_number = serializers.RegexField(
        regex=r'^\d{10}$',
        error_messages={
            'invalid': 'Phone number must be exactly 10 digits',
            'required': 'Phone number is required'
        }
    )

    class Meta:
        model = Candidate
        fields = ['name', 'age', 'gender', 'email', 'phone_number']
        extra_kwargs = {
            'name': {
                'error_messages': {
                    'required': 'Name is required',
                    'blank': 'Name cannot be empty'
                }
            }
        }

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Name should contain only letters and spaces")
        return value.strip()

    def validate_email(self, value):
        if Candidate.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value.lower()


class CandidateUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        error_messages={
            'invalid': 'Please enter a valid email address'
        }
    )
    gender = serializers.ChoiceField(
        choices=Candidate.GENDER_CHOICES,
        required=False,
        error_messages={
            'invalid_choice': 'Gender must be one of: M (Male), F (Female), O (Other)'
        }
    )
    age = serializers.IntegerField(
        min_value=18,
        max_value=100,
        required=False,
        error_messages={
            'min_value': 'Age must be at least 18',
            'max_value': 'Age cannot be more than 100',
            'invalid': 'Age must be a valid integer'
        }
    )
    phone_number = serializers.RegexField(
        regex=r'^\d{10}$',
        required=False,
        error_messages={
            'invalid': 'Phone number must be exactly 10 digits'
        }
    )

    class Meta:
        model = Candidate
        fields = ['name', 'age', 'gender', 'email', 'phone_number']
        extra_kwargs = {
            'name': {
                'required': False,
                'error_messages': {
                    'blank': 'Name cannot be empty'
                }
            }
        }

    def validate_name(self, value):
        if value and not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        if value and not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Name should contain only letters and spaces")
        return value.strip() if value else value

    def validate_email(self, value):
        if value:
            # Check if email exists for other candidates
            if Candidate.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Email already exists")
            return value.lower()
        return value
    

class CandidateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'age', 'gender', 'email', 'phone_number']