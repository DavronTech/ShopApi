from django.shortcuts import render
from .models import NEW, CODE_VERIFY,VIA_EMAIL,VIA_PHONE
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView
from .serilazer import SigUpSerilazer, ChangInfoSerilazer, AddPhotoSerilazer
from .models import CustomUser
from rest_framework import permissions
from datetime import timedelta,datetime
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail



class SignUpView(CreateAPIView):
    serializer_class = SigUpSerilazer
    queryset = CustomUser.objects.all()


class CodeVerifyView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()

    def post(self,request):
        code = request.data.get('code')
        user = request.user

        codes = user.codes.all().filter(code=code, used=False, expiration_time__gte  = datetime.now()).first() 

        if codes is None:
            raise ValidationError('Kod yaroqsiz yoki eskirgan')

        if user.auth_statsus == NEW:
            user.auth_status == CODE_VERIFY
            codes.used = True
            user.save()
            code.save()

        return  Response({
            'msg': 'kod tasdiqlandi',
            'auth_statsus': user.auth_status
        })

class GetNewCodeView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.auth_status != NEW:
            raise ValidationError('sizda bu holat taqiqlangan')

        codes = user.codes.all().filter(used=False, expiration_time__gte  = datetime.now()).first()

        if user.auth_taype == VIA_EMAIL:
            code = user.generated_code(user.auth_taype)

            send_mail(
                subject="Tasdiqlash kodi",
                message=f"Sizning tasdiqlash kodingiz: {code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

        elif user.auth_taype == VIA_PHONE:
            code = user.generated_code(user.auth_taype)

            # sms orqali yuborish
           # send_sms(
           #     phone=user.phone,
           #     message=f"Sizning tasdiqlash kodingiz: {code}"
           # )          

        else:
            raise ValidationError('telefon raqam yoki email hato kiritigiz')

        return Response({
            'msg': 'kod yuborildi'

        })
        
class ChangeInfoView(UpdateAPIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = ChangInfoSerilazer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user


class AddPhotoView(UpdateAPIView):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class = AddPhotoSerilazer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user