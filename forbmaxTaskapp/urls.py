from django.urls import path
from . import views

urlpatterns = [
    path('user/creates/', views.UserRegistrationView.as_view(), name='user-create'),
    path('user/login/', views.UserLoginView.as_view(), name='login'),
    path('group/create/', views.GroupCreateView.as_view(), name='group-create'),
    path('content/create/', views.ContentCreateView.as_view(), name='content-create'),
    path('content/view/', views.ContentView.as_view(), name='content-view'),
]
