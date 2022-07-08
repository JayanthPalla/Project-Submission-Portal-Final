from urllib import response
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser, FileUploadParser
from .serializers import ProjectRegistrationSerializer, ProjectSubmissionSerializer
from .models import User, ProjectRegistration, ProjectSubmission
from .mails import send_verify_mail, send_password_mail
from project1.settings import key, MEDIA_ROOT
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import jwt, datetime
from .logs import logger
from rest_framework.views import APIView
import pytz


def display_dashboard(request):
    token = request.COOKIES.get('token', None)

    if token==None:
        logger.error("Token not exist")
        return redirect("login-page")

    try:
        payload = jwt.decode(token, key, algorithms=['HS256'])
        print(payload)
    except jwt.ExpiredSignatureError:
        return redirect("login-page")

    user = User.objects.filter(email=payload['email']).first()

    if payload['role'] == 'student':
        faculty = User.objects.filter(role = 'faculty', branch = user.branch).all()
        projects = ProjectSubmission.objects.filter(clg_id = user.clg_id).all()

        return render(request, 'project1/student-dashboard.html', {'user':user, 'faculty':faculty, 'projects':projects})
    elif payload['role'] == 'faculty':
        return render(request, 'project1/faculty-dashboard.html', {'user':user})

def display_scoreboard(request):
    token = request.COOKIES.get('token', None)

    if token==None:
        logger.error("Token not exist")
        return redirect("login-page")

    try:
        payload = jwt.decode(token, key, algorithms=['HS256'])
        print(payload)
    except jwt.ExpiredSignatureError:
        return redirect("login-page")

    user = User.objects.filter(email=payload['email']).first()

    if payload['role'] == 'student':
        return render(request, 'project1/student_scoreboard.html', {'user':user})
    elif payload['role'] == 'faculty':
        return render(request, 'project1/faculty_scoreboard.html', {'user':user})


def display_about(request):
    return render(request, 'project1/about.html')


#student apis

def register_project(request):
    serializer = ProjectRegistrationSerializer(data=request.POST)

    already_exist = ProjectRegistration.objects.filter(clg_id = request.POST.get('clg_id')).exists()

    if already_exist:
        messages.error(request, "Already registered before")

    elif serializer.is_valid():
        serializer.save()
        logger.info(serializer.data)
        messages.success(request, "Project registration completed successfully")
    else:
        logger.error(serializer.errors)
        messages.error(request, "Project registration unsuccessful")

    return redirect('dashboard')

@api_view(['GET', 'POST'])
def submit_project(request):
    if request.method == 'POST':
        parser_class = (FileUploadParser, )
        serializer = ProjectSubmissionSerializer(data=request.data)

        print('\n\n-->',datetime.datetime.now(pytz.utc),'\n\n')

        if serializer.is_valid():
            serializer.save()
            logger.info(serializer.data)
            messages.success(request, "Project submitted successfully")
        else:
            logger.error(serializer.errors)
            messages.error(request, "Project submition failed")

        return redirect('dashboard')

@api_view(['GET'])
def download_project(request):
    project = ProjectSubmission.objects.filter(project_id = request.query_params['id']).first()
    file_path = MEDIA_ROOT + str(project.project_file)
    response = FileResponse(open(file_path,'rb'))

    return response

# class FileUploadView(APIView):
#     permission_classes = []
#     parser_class = (FileUploadParser,)

#     def post(self, request, *args, **kwargs):

#       file_serializer = ProjectSubmissionSerializer(data=request.data)

#       if file_serializer.is_valid():
#           file_serializer.save()
#           return Response(file_serializer.data, status=status.HTTP_201_CREATED)
#       else:
#           return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)