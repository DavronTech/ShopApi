from django.shortcuts import render
from .models import NEW, CODE_VERIFY
from rest_framework.generics import CreateAPIView, GenericAPIView
from .serilazer import SigUpSerilazer
from .models import CustomUser
from rest_framework import permissions



class SignUpView(CreateAPIView):
    serializer_class = SigUpSerilazer
    queryset = CustomUser.objects.all()


# Create your views here.
