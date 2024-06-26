from functools import partial
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from .serializers import UserSerializer, UpdateProfileSerializer
from .models import User
from .mails import send_verify_mail, send_password_mail
from project1.settings import key
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import jwt, datetime
from .logs import logger
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

# Create your views here.



def generate_url(email_id, action):
    payload = {
        'email' : email_id,
        'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        'iat' : datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, key, algorithm='HS256') # .decode('utf-8')
    if action == 'verify':
        url = 'http://localhost:8000/user/verify_user?token='+token
    elif action == 'reset':
        url = 'http://localhost:8000/user/reset_password?token='+token
    
    logger.info("Url is created \n url--> "+url)

    return url

def home(request):
    return redirect("login-page")

@api_view(['GET', 'POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)

        if request.POST.get('password') != request.POST.get('confirm_password'):
            logger.info("Different passwords entered")
            messages.warning(request, "Password and confirm password must be same")
            # raise serializer.ValidationError('Password must be same')

        if serializer.is_valid():
            serializer.save()
            logger.info("user created with is_verified value as False")

            # email = user.email
            # url = generate_url(email, 'verify')
            # send_verify_mail(url,email)
            messages.success(request, "User created successfully")

        else:
            logger.error(serializer.errors)
            messages.error(request, "This email already exists")
        
        return redirect('register-page')
        # return Response(serializer.errors)
    else:
        logger.info("Request for fetching Register-page.html")
        return render(request, 'project1/Register-page.html')

# @api_view(['POST', 'GET'])
# def verify_user(request):
#     token = request.query_params['token']
#     payload = jwt.decode(token, key, algorithms=['HS256'])
#     email =  payload['email']

#     # user = User.objects.get(email = email)
#     user = User.objects.filter(email = email).first()

#     if user is None:
#         logger.error("User verification unsuccessful")
#         raise AuthenticationFailed('Un authorised')

#     User.objects.filter(email=email).update(is_verified = True)
    
#     logger.info("User verified and is_verified field value updated to",user.is_verified)

#     messages.success(request, "User verified successfully")
#     return redirect('http://localhost:8000/user/login/')

@api_view(['GET','POST'])
def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(email=email).first()

        print("email is ",email)
        print("user is ",user)

        if user is None:
            logger.error("User not found")
            # raise AuthenticationFailed('User not found')
            messages.error(request, 'Enter valid email and password')
            return redirect('login-page')

        if not user.check_password(password):
            logger.error("Incorrect password")
            # raise AuthenticationFailed('Incorrect password')
            messages.error(request, 'Enter valid email and password')
            return redirect('login-page')
            

        if getattr(user, 'is_verified') != True:
            logger.error("Current User is not verified")
            # raise AuthenticationFailed('Current User is not verified')
            messages.error(request, 'Enter valid email and password')
            return redirect('login-page')


        remember = request.POST.get('remember')
        exp = datetime.datetime.utcnow() + (datetime.timedelta(minutes=60) if remember == None else datetime.timedelta(hours=24))

        payload = {
            # 'id':user.id,
            'email':email,
            'role':user.role,
            'exp':exp,
            'iat':datetime.datetime.utcnow()
        }

        
        token = jwt.encode(payload, key, algorithm ='HS256') #.decode('utf-8')

        logger.info("login jwt token created \ntoken -->",token)


        response = HttpResponseRedirect("http://localhost:8000/user/user-dashboard/")

        response.set_cookie(key='token', value=token, httponly=True)
        logger.info("Token set to cookies with key 'token'")
        
        return response

    else:
        logger.info("Request for fetching login-page.html")
        return render(request, 'project1/login-page.html')



@api_view(['GET', 'POST'])
def forgot_password(request):
    if request.method == 'POST':
        email = request.data['email']

        if User.objects.filter(email=email).exists():
            # url = generate_url(email, 'reset')
            # send_password_mail(url,email)
            # return render(request, 'project1/forget_password.html',{'status':'mail sent successfully'})
            messages.success(request, "Reset password mail sent successfully")
            return redirect('reset-pswd')
            
        else:
            logger.error("Forgot password mail doesn't send as the user not exists")
            # return render(request, 'project1/forget_password.html',{'status':'User not exists'})
            messages.error(request, "User not exists")
            return redirect('register-page')

    else:
        logger.info("Request for fetching forget_password.html")
        return render(request, 'project1/forget_password.html')

        

@api_view(['GET', 'POST'])
def reset_password(request):
    token = request.query_params['token']

    if request.method == 'POST':
        
        payload = jwt.decode(token, key, algorithms=['HS256'])

        user = User.objects.get(email = payload['email'])

        if user is None:
            raise AuthenticationFailed('Un authorised')

        print(request.data)
        pswd1 = request.data['new_password']
        pswd2 = request.data['confirm_password']

        if pswd1==pswd2:
            user.set_password(pswd1)
            user.save()
            messages.success(request, "Password reset successfully")

            return redirect("login-page")
            # return Response({'msg':'Password updated!'}, status=status.HTTP_200_OK)
        return Response({'msg':"confirm password doesn't match"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.info("Request for fetching reset_password.html")
        return render(request, 'project1/reset_password.html',{'token': token})

@api_view(['GET', 'POST'])
def logout_user(request):
        response = HttpResponseRedirect("http://localhost:8000/user/login/")
        response.delete_cookie('token')
        logger.info("Session expired")
        return response


def get_user(request):
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

        print(user)

        logger.info("Request for User details")
        return render(request, 'project1/profile-page.html',{'user':user})

class UpdateProfileView(generics.UpdateAPIView):
    # queryset = User.objects.all()
    # permission_classes = (IsAuthenticated,)
    serializer_class = UpdateProfileSerializer

@api_view(['GET', 'POST'])
def edit_profile(request):
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

    if request.method == "POST":
        print('\n\n',dict(request.data),'\n\n')
        serializer_class = UpdateProfileSerializer
        serializer = UpdateProfileSerializer(user, data = request.data, partial = True)
        print("serializer created")

        if serializer.is_valid():
            print("inside if block")
            serializer.save()
            logger.info("User details updated")

        else:
            print("inside else block")
            logger.error(serializer.errors)
            messages.error(request, "User details not updated")

        print("return statement")
        return redirect('edit-profile')
        
    else:
        return render(request, 'project1/edit-profile.html',{'user':user})