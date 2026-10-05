import re
from rest_framework.exceptions import ValidationError



email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
phone_regex = re.compile(r'^\+998\s\d{2}\s\d{3}\s\d{2}\s\d{2}$')


def email_phone_regex(user_input):

    if re.fullmatch(email_regex , user_input):
        return 'email'

    elif re.fullmatch(phone_regex,user_input):
        return 'phone'

    else:
        raise ValidationError('Siz hato email yoki telefon raqam kiritingiz')

