from django.views.decorators import csrf
from rest_framework import decorators, status

from . import forms
import django.http

@csrf.csrf_exempt
def validate_chat_form(request):
    context = {}
    if forms.CreateChatForm(request.data).is_valid():
        context.update({'is_valid': True})
    return django.http.JsonResponse(context, status=status.HTTP_200_OK)

@csrf.csrf_exempt
def validate_login_form(request):
    context = {}
    if forms.LoginForm(request.data).is_valid():
        context.update({'is_valid': True})
    return django.http.JsonResponse(context, status=status.HTTP_200_OK)

@csrf.csrf_exempt
def validate_register_form(request):
    context = {}
    if forms.CreateUserForm(request.data).is_valid():
        context.update({'is_valid': True})
    return django.http.JsonResponse(context, status=status.HTTP_200_OK)

@csrf.csrf_exempt
def validate_edit_user_form(request):
    context = {}
    if forms.EditUserForm(request.data).is_valid():
        context.update({'is_valid': True})
    return django.http.JsonResponse(context, status=status.HTTP_200_OK)

