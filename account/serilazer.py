from rest_framework import serializers
from .models import CustomUser
from base.utils import email_phone_regex
from .models import VIA_EMAIL , VIA_PHONE
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail

class SigUpSerilazer(serializers.ModelSerializer):
    email_or_prhone_number = serializers.CharField(write_only = True)



    class Meta:
        model = CustomUser
        fields  = ['auth_taype', 'auth_status', 'email_or_prhone_number ']

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.save()


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

        return user


    def to_representation(self, instance):
        data =  super().to_representation(instance)

        return {
            'tokens':instance.token(),
            'data': data
        }



    def validate(self, attrs):
        user_input = attrs.get('email_or_prhone_number ')

        user_input_taype = email_phone_regex(user_input)

        if user_input_taype == 'email':
           data = {
               'email': user_input,
               'auth_taype': VIA_EMAIL
           }

        elif  user_input_taype == 'phone':
           data = {
               'phone': user_input,
               'auth_taype': VIA_PHONE
           }

        else:
            raise ValidationError('siz hato email yoki telefon raqam kiritingiz')

        
        return data

        
        