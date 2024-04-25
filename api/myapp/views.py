from datetime import datetime
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.core.checks import messages
from django.db.models import Model
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView
from rest_framework import request
from . import forms
from django.http import JsonResponse
from .models import *
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO
from .forms import LandmarkForm, RouteForm

class MainPage(TemplateView):
    template_name = 'main.html'

class Signin(LoginView):
    template_name = "signin.html"

    def get_success_url(self):
        return reverse('create')

class Signup(CreateView):
    model = settings.AUTH_USER_MODEL
    template_name = "signup.html"
    form_class = forms.SignupForm
    success_url = reverse_lazy('main')




class Create(TemplateView):
    template_name = 'create.html'


class Favorite(TemplateView):
    template_name = 'favorite.html'


class HotelReserv(TemplateView):
    template_name = 'hotelreserv.html'


class TransReserv(TemplateView):
    template_name = 'transreserv.html'


class Personal(TemplateView):
    template_name = 'personal.html'
# Create your views here.

class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)

def add_route(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        if name:
            route = Place.objects.create(name=name)
            return JsonResponse({'success': True, 'route_name': route.name})
    return JsonResponse({'success': False})

def filter_models(request):
    if request.method == 'POST':
        city_name = request.POST.get('city', '').lower()  # Получаем введенный город
        try:
            city = City.objects.get(name=city_name)  # Пытаемся найти соответствующий город в базе данных
            models = Model.objects.filter(city=city)  # Фильтруем модели по найденному городу
            model_names = [model.name for model in models]  # Получаем имена моделей
            return JsonResponse({'success': True, 'models': model_names})
        except City.DoesNotExist:
            pass  # Если город не найден, ничего не возвращаем
    return JsonResponse({'success': False})


def get_coordinates(place):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey=ВАШ_API_КЛЮЧ&format=json&geocode={place}"
    response = requests.get(url)
    data = response.json()
    coordinates = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
    return coordinates.split(" ")


def build_route(places):
    coordinates = []
    for place in places:
        coordinates.append(get_coordinates(place))

    url = "https://api.routing.yandex.net/v1.0/route/"
    params = {
        "apikey": "ВАШ_API_КЛЮЧ",
        "format": "json",
        "lang": "ru_RU",
        "routingMode": "auto",
        "waypoints": ";".join([",".join(coord) for coord in coordinates])
    }
    response = requests.get(url, params=params)
    data = response.json()

    return data

def show_route(request):
    if request.method == 'POST':
        places = request.POST.getlist('places[]')  # Получаем список мест из формы
        route_data = build_route(places)
        return JsonResponse(route_data)  # Возвращаем данные о маршруте в формате JSON
    else:
        return JsonResponse({'error': 'Метод GET не поддерживается'})  # Обработка случая, если используется GET запрос


def save_favorite_transport_route(request):
    if request.method == 'POST':
        route_id = request.POST.get('route_id', None)
        if route_id:
            # Получаем маршрут транспорта по его ID
            try:
                transport_route = TransportRoute.objects.get(pk=route_id)
            except TransportRoute.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Маршрут не найден'})

            # Создаем новую запись в модели FavoriteRoute на основе маршрута транспорта
            favorite_route = FavoriteRoute.objects.create(
                name=transport_route.name,
                route=f"Из {transport_route.departure.name} в {transport_route.arrival.name}",
                # Дополнительные данные о маршруте, которые вы хотите сохранить
            )
            favorite_route.save()
            return JsonResponse({'success': True, 'message': 'Маршрут сохранен в избранные'})
    return JsonResponse({'success': False, 'message': 'Неверный запрос'})

def calculate_trip_cost(selected_attractions, selected_hotel, selected_tickets):
    # Получение данных о выбранных достопримечательностях
    attractions = Place.objects.filter(id__in=selected_attractions)
    attractions_cost = sum(attraction.cost for attraction in attractions)

    # Получение данных о выбранном отеле
    hotel = Hotel.objects.get(id=selected_hotel)
    hotel_cost = hotel.cost_per_night  # Предположим, что стоимость отеля за ночь

    # Получение данных о выбранных билетах
    tickets = TransportRoute.objects.filter(id__in=selected_tickets)
    tickets_cost = sum(ticket.price for ticket in tickets)

    # Расчет общей стоимости поездки
    total_cost = attractions_cost + hotel_cost + tickets_cost

    return total_cost

def filter_hotels(num_people, star_rating, check_in_date, check_out_date):
    if request.method == 'GET':
        num_people = request.GET.get('num_people')
        star_rating = request.GET.get('star_rating')
        check_in_date = request.GET.get('check_in_date')
        check_out_date = request.GET.get('check_out_date')
    # Преобразование дат в формат DateTime, если это необходимо
    check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
    check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')

    # Фильтрация отелей по количеству звезд и доступным номерам
    hotels = Hotel.objects.filter(star_rating__gte=star_rating, available_rooms__gte=num_people)

    # Фильтрация отелей по датам доступности
    hotels = hotels.filter(
        room_availability__check_in_date__lte=check_in_date,
        room_availability__check_out_date__gte=check_out_date
    )

    return hotels

def filter_transport(request):
    if request.method == 'GET':
        transport_type = request.GET.get('transport_type')
        seats = request.GET.get('seats')
        departure_city = request.GET.get('departure_city')
        arrival_city = request.GET.get('arrival_city')
        departure_date = request.GET.get('departure_date')
        arrival_date = request.GET.get('arrival_date')

        transport = filter_transport(transport_type, seats, departure_city, arrival_city, departure_date, arrival_date)
        # Возвращаем отфильтрованный транспорт в контексте
        return render(request, 'filtered_transport.html', {'transport': transport})

def handle_edit_button(request, action):
    if action == 'sightseeing':
        # Перенаправляем на страницу выбора достопримечательностей
        return redirect('choose_sightseeing')
    elif action == 'accommodation':
        # Перенаправляем на страницу бронирования жилья
        return redirect('book_accommodation')
    elif action == 'transport':
        # Перенаправляем на страницу бронирования транспорта
        return redirect('book_transport')
    else:
        # В случае некорректного действия перенаправляем на главную страницу
        return redirect('main')

def generate_pdf(request):
    # Получаем данные формы избранного маршрута
    # Здесь вы должны получить данные из вашей формы избранного маршрута

    # Создаем PDF-документ
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Добавляем информацию о маршруте в PDF
    c.drawString(100, 750, "Избранный маршрут")
    # Здесь вы можете добавить остальные данные маршрута

    # Сохраняем PDF-документ
    c.showPage()
    c.save()

    # Получаем содержимое буфера и возвращаем PDF-файл в ответе
    pdf_data = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="favorite_route.pdf"'
    response.write(pdf_data)
    return response


def get_landmarks(latitude, longitude, radius=1000, lang='ru_RU'):
    api_key = 'YOUR_API_KEY'  # Замените YOUR_API_KEY на ваш API-ключ от Яндекс.Карт
    url = f'https://search-maps.yandex.ru/v1/?apikey={api_key}&text=landmark&ll={longitude},{latitude}&spn=0.1,0.1&results=10&lang={lang}&type=geo'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        landmarks = data.get('features', [])
        return landmarks
    else:
        print("Ошибка при запросе к Яндекс.Картам:", response.status_code)
        return []


def landmarks_view(request):
    if request.method == 'POST':
        form = LandmarkForm(request.POST)
        if form.is_valid():
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            landmarks = get_landmarks(latitude, longitude)
            return render(request, 'landmarks.html', {'landmarks': landmarks})
    else:
        form = LandmarkForm()
    return render(request, 'landmark_form.html', {'form': form})


def get_routes(origin, destination, mode='auto'):
    api_key = 'YOUR_API_KEY'  # Замените YOUR_API_KEY на ваш API-ключ от Яндекс.Карт
    url = f'https://api.routing.yandex.net/v2.1/{mode}/?apikey={api_key}&origin={origin}&destination={destination}&lang=ru-RU'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        routes = data.get('routes', [])
        return routes
    else:
        print("Ошибка при запросе к Яндекс.Картам:", response.status_code)
        return []


def routes_view(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            routes = get_routes(origin, destination)
            return render(request, 'routes.html', {'routes': routes})
    else:
        form = RouteForm()
    return render(request, 'route_form.html', {'form': form})

def get_hotels(latitude, longitude, lang='ru_RU'):
    api_key = 'YOUR_API_KEY'  # Замените YOUR_API_KEY на ваш API-ключ от Яндекс.Карт
    url = f'https://search-maps.yandex.ru/v1/?apikey={api_key}&text=hotel&ll={longitude},{latitude}&spn=0.1,0.1&results=10&lang={lang}&type=geo'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        hotels = data.get('features', [])
        return hotels
    else:
        print("Ошибка при запросе к Яндекс.Картам:", response.status_code)
        return []

