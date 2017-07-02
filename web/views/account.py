# coding:utf-8
import logging

from django.contrib import auth
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from web.forms import account
from web.models.res import Quota
from web.models.rest.proto import JsonResponse
from web.utils import random_util, mail_sender
from web.utils import zk_util

# Account management
logger = logging.getLogger(__name__)


def check_duplicate(request):
    username = request.GET.get('username')
    email = request.GET.get('email')
    user = None
    if username and email:
        user = User.objects.filter(
            username=username,
            email=email
        )
    elif username:
        user = User.objects.filter(
            username=username,
        )
    elif email:
        user = User.objects.filter(
            email=email
        )
    if user:
        return HttpResponse("true")
    return HttpResponse("false")


@transaction.atomic
def register(request):
    if request.method == 'POST':
        signup_form = account.SignupForm(request.POST)
        print('x' * 100)
        print(signup_form)
        print(signup_form.is_valid())
        print('x' * 100)
        if signup_form.is_valid():
            signup_info = signup_form.cleaned_data
            print('x' * 100)
            print(signup_info['username'])
            print('x' * 100)
            user = User.objects.create_user(
                username=signup_info['username'],
                email=signup_info['email'],
                password=signup_info['password']
            )
            user.save()
            # default memory limit
            quota = Quota(user=user, memory=4096)
            quota.save()
            zk_util.init_schema(user.username)
            return HttpResponseRedirect(reverse('web:login'))
    else:
        signup_form = account.SignupForm()
    return render(request, 'login.html', {'form': signup_form})


def login(request):
    if request.method == 'POST':
        login_form = account.LoginForm(request.POST)
        if login_form.is_valid():
            login_info = login_form.cleaned_data
            print(login_info)
            user = auth.authenticate(
                username=login_info['username'],
                password=login_info['password']
            )
            print(user)
            if user and user.is_active:
                auth.login(request, user)
                next_url = request.POST.get('next')
                if next_url:
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect(reverse('web:index'))
            else:
                login_form.errors[""] = "Wrong username or password."
    else:
        login_form = account.LoginForm()
    return render(request, 'login.html',
                  {'form': login_form})


def forgot(request):
    if request.method == 'POST':
        forgot_form = account.ForgotForm(request.POST)
        if forgot_form.is_valid():
            forgot_info = forgot_form.cleaned_data
            email = forgot_info['email']
            users = User.objects.filter(email=email)
            if users and users[0].is_active:
                pwd = random_util.gen_str(8)
                users[0].set_password(pwd)
                users[0].save()
                retry = 0
                while True:
                    success = mail_sender.send(
                        users[0].email,
                        "Password Reset Info",
                        "Your password bas been reset! New Password :" + pwd)

                    retry += 1
                    if success or retry > 2:
                        break
                if success:
                    return JsonResponse(
                            True,
                            'Send Success!Please check you emailbox.').toJSON()
                return JsonResponse(False, 'Send Failed!').toJSON()
            else:
                return JsonResponse(
                        False,
                        'User does not exist or is disabled.').toJSON()
    else:
        forgot_form = account.ForgotForm()
    return render(request, 'web/account/forgot.html', {'form': forgot_form})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('web:login'))


def profile(request):
    if request.method == 'POST':
        forgot_form = account.ForgotForm(request.POST)
        if forgot_form.is_valid():
            forgot_info = forgot_form.cleaned_data
            email = forgot_info['email']
            users = User.objects.filter(email=email)
            if users and users[0].is_active:
                pwd = random_util.gen_str(8)
                users[0].set_password(pwd)
                users[0].save()
                retry = 0
                while True:
                    success = mail_sender.send(
                        users[0].email,
                        "Password Reset Info",
                        "Your password bas been reset! New Password :" + pwd)

                    retry += 1
                    if success or retry > 2:
                        break
                if success:
                    return JsonResponse(
                            True,
                            'Send Success!Please check you emailbox.').toJSON()
                return JsonResponse(False, 'Send Failed!').toJSON()
            else:
                return JsonResponse(
                        False,
                        'User does not exist or is disabled.').toJSON()
    else:
        forgot_form = account.ForgotForm()
    return render(request, 'profile.html', {'form': forgot_form})
