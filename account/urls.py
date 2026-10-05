from django.urls import path
from .views import SignUpView, CodeVerifyView, GetNewCodeView, ChangeInfoView, AddPhotoView


urlpatterns = [
    path('signup/',SignUpView.as_view()),
    path('code-verifay/',CodeVerifyView.as_view()),
    path('get-new-code/',GetNewCodeView.as_view()),
    path('changeinfo/',ChangeInfoView.as_view()),
    path('photo/',AddPhotoView.as_view()),

    


]