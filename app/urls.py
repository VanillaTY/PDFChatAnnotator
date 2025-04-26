from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submitCard/', views.submitCard, name='submitCard'),
    path('receiveMessage/', views.receiveMessage, name='receiveMessage'),
    path('fileHandle/', views.fileHandle, name='fileHandle'),
]