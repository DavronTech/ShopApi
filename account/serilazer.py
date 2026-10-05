from rest_framework import serializers
from .models import CustomUser
from base.utils import email_phone_regex
from .models import VIA_EMAIL , VIA_PHONE, DONE, CODE_VERIFY,NEW, PHOTO_DONE
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from datetime import datetime

class SigUpSerilazer(serializers.ModelSerializer):
    email_or_prhone_number = serializers.CharField(write_only = True)



    class Meta:
        model = CustomUser
        fields  = ['id','auth_taype', 'auth_status', 'email_or_prhone_number ']
        read_only_fields = ['id','auth_taype', 'auth_status']

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



    def validate(self, attrs):


    
        user_input = attrs.get('email_or_prhone_number ')

        user = CustomUser.objects.filter(Q(phone_number = user_input)| Q( email = user_input)).first()
        if user:
            if user.auth_status in [DONE,PHOTO_DONE]:
                raise ValidationError("email yoki telefon raqam avval bizdan royxatdan otgan ")
            else:
                self.send_code_chek(user)
                user.delete()


    
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

    def send_code_chek(self,user):
        codes = user.codes.all().filter(used = False, expire_time__gte = datetime.now()).first()
        if codes:
            raise ValidationError('sizda aktiv kod bor ')

        
    
    def to_representation(self, instance):
        data =  super().to_representation(instance)

        return {
            'tokens':instance.token(),
            'data': data
        }


class ChangInfoSerilazer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only = True)
    password = serializers.CharField(write_only = True)

    class Meta:
        model = CustomUser
        fields = ['id','auth_status', 'auth_taype','first_name', 'last_name', 'username', 'password', 'confirm_password']
        read_only_fields = ['id','auth_status', 'auth_taype']


    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Parollar mos emas")

        return attrs

    def update(self, instance, validated_data):
        if instance.auth_status != CODE_VERIFY:
            raise ValidationError('siz toliq royxatdan otmagansiz')
        
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')
        instance.password = instance.set_password( validated_data.get('password'))
        instance.auth_status = DONE
        instance.save()

        return instance
    

class AddPhotoSerilazer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id','auth_status', 'auth_taype','first_name', 'last_name', 'username','photo']
        read_only_fields = ['id','auth_status', 'auth_taype','first_name', 'last_name', 'username',]




    def update(self, instance, validated_data):
        if instance.auth_status != DONE:
            raise ValidationError("Siz toliq royxatdan otmagansiz")
        
        image = validated_data.get('image')
        if image:
            raise ValidationError('siz toliq royxatdan otmagansiz')
        
        instance.image = image
        
        instance.auth_status = PHOTO_DONE
        instance.save()

        return instance
