# from django.contrib import admin
from django.urls import path
from .views import  edit_profile, login_user, register_user, forgot_password, logout_user, get_user, reset_password #, change_password , verify_user
from .site_apis import display_dashboard, display_about, display_scoreboard, register_project , submit_project

urlpatterns = [
    path('register/', register_user, name="register-page"),
    path('login/', login_user, name="login-page"),
    path('myProfile/', get_user, name="profile-page"),
    path('logout/', logout_user, name="logout"),
    # path('verify_user/', verify_user),
    # path('change_password', change_password),
    path('forgot_password/', forgot_password, name="forgot-pswd"),
    path('reset_password', reset_password, name="reset-pswd"),
    path('editProfile/', edit_profile, name="edit-profile"),
    path('user-dashboard/', display_dashboard, name="dashboard"),
    path('scoreboard/', display_scoreboard, name="scoreboard"),
    path('about-Devs/', display_about, name="about-page"),

    path('register_project', register_project, name="register_project"),
    path('submit_project', submit_project, name="submit_project")
]