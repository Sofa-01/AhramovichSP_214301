from django.urls import path
from . import views
from .views import show_route

urlpatterns = [
    path('', views.MainPage.as_view(), name='main'),
    path('signin/', views.Signin.as_view(), name='signin'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('create/', views.Create.as_view(), name='create'),
    path('favorite/', views.Favorite.as_view(), name='favorite'),
    path('hotelreserv/', views.HotelReserv.as_view(), name='hotelreserv'),
    path('transreserv/', views.TransReserv.as_view(), name='transreserv'),
    path('personal/', views.Personal.as_view(), name='personal'),
    path('show_route/', show_route, name='show_route'),
    path('landmarks/', views.landmarks_view, name='landmarks'),
    path('routes/', views.routes_view, name='routes'),
]

