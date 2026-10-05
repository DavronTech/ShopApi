from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import BaseModel
from datetime import timedelta,datetime
from shop.settings import EMAIL_EXPIRE_TIME,PHONE_EXPIRE_TIME
import uuid
import random
from rest_framework_simplejwt.tokens import RefreshToken

NEW, CODE_VERIFY, DONE, PHOTO_DONE = ('new', 'code_verify', 'done', 'photo_done')

VIA_PHONE, VIA_EMAIL = ('via_phone', 'via_email')

SELLER, CUSTOMER = ('seller', 'customer')


class CustomUser(AbstractUser, BaseModel):


    AUTH_STAUS = (
        (NEW, NEW),
        (CODE_VERIFY, CODE_VERIFY),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE),

    )

    AUTH_TAYPE = (
        (VIA_EMAIL, VIA_EMAIL)
        (VIA_PHONE,VIA_PHONE)

    )

    AUTH_ROLE = (
        (SELLER,SELLER)
        (CUSTOMER,CUSTOMER)
    )


    phone_number = models.CharField(max_length=13, unique=True, blank=True,null=True, )
    email = models.CharField(max_length=13, unique=True, blank=True,null=True, )
    auth_status = models.CharField(max_length=20, choices=AUTH_STAUS, default=NEW )
    auth_taype = models.CharField(max_length=30, choices=AUTH_TAYPE)
    auth_role = models.CharField(max_length=20, choices=AUTH_ROLE)
    image = models.ImageField(upload_to='/users', blank=True, null=True)
    addres = models.CharField(max_length=120, blank=True,null=True)


    def __str__(self):
        return self.username

    def chek_username(self):
        if not self.username:
            ud = str(uuid.uuid4())
            temp_username = f"username{ud[ud.rfind('-')]}"

            while CustomUser.objects.filter(username=temp_username).exists():
                temp_username += str(random.randint(0, 9))

            self.username = temp_username

    def chek_pass(self):
        if not self.password:
            ud = str(uuid.uuid4())
            temp_password = f"password{ud[ud.rfind('-'):]}"
            self.password = temp_password

    def hashing_pass(self):
        if not  self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)


    def email_normalize(self):
        if self.email:
            temp_email = self.email.lower()
            self.email = temp_email

    def token(self):
        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'accses': str(refresh.access_token)

        }


    def generated_code(self, verifay_taype):
        code = random.randint(1000,9999)

        Verifay.objects.create(
            code=code,
            user = self,
            verifay_taype = verifay_taype

        )
        return code

    def save(self,*args, **kwargs ):
        self.chek_username()
        self.chek_pass()
        self.hashing_pass()
        self.email_normalize()
        super().save(*args, **kwargs)

    

 

class Verifay(BaseModel):
    VERIFAY_TAYPE = (
            (VIA_EMAIL, VIA_EMAIL)
            (VIA_PHONE,VIA_PHONE)
    )

    verifay_taype = models.CharField(max_length=30, choices=VERIFAY_TAYPE)
    used = models.BooleanField(default=False)
    expire_time = models.DateTimeField()
    code = models.CharField(max_length=4)
    user = models.CharField(CustomUser, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.user.username}-------{self.code}"


    def save(self, *args, **kwargs):

        if self.verifay_taype ==    VIA_EMAIL:
            self.expire_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE_TIME)

        else:
            self.verifay_taype = datetime.now() + timedelta(minutes=PHONE_EXPIRE_TIME)



        super().save(*args, **kwargs)


    

# Create your models here.
