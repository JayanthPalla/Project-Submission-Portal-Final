from rest_framework import serializers
from .models import User, ProjectRegistration, ProjectSubmission


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'clg_id', 'first_name', 'last_name', 'role', 'gender', 'email', 'address', 'branch', 'year', 'dob', 'mobile', 'password'] #, 'is_active', 'is_verified'] , 'profile_pic'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class UpdateProfileSerializer(serializers.ModelSerializer):
    # first_name = serializers.CharField(write_only=True, required=True)
    # last_name = serializers.CharField(write_only=True, required=True)
    # gender = serializers.CharField(write_only=True, required=True)
    # dob = serializers.CharField(write_only=True, required=True)
    # mobile = serializers.CharField(write_only=True, required=True)
    # address = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'dob', 'branch', 'year', 'mobile', 'address')


    def update(self, instance, validated_data):
        print("---->", validated_data,"--->", instance)
        instance.first_name=validated_data.get('first_name', instance.first_name)
        instance.last_name=validated_data.get('last_name', instance.last_name)
        # instance.gender=validated_data['gender']
        instance.dob=validated_data.get('dob', instance.dob)
        instance.mobile=validated_data.get('mobile', instance.mobile)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.year = validated_data.get('year', instance.year)
        instance.address=validated_data.get('address', instance.address)
        instance.save()
        
        return instance

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required = True)
    password2 = serializers.CharField(write_only = True, required = True)
    old_password = serializers.CharField(write_only = True, required = True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password":"Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class ProjectRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRegistration
        fields = ('clg_id', 'branch', 'faculty', 'aca_year')


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    # project_file = serializers.FileField(read_only=True)
    class Meta:
        model = ProjectSubmission
        fields = ('clg_id', 'project_id', 'project_title', 'individual_or_team', 'project_description', 'project_file')

   