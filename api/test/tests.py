import unittest
from django.test import TestCase, RequestFactory, Client
from unittest.mock import patch
from api.myapp.models import *
from api.myapp.views import *
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.urls import reverse

#тесты создания маршрута
##добавить маршрут
class AddRouteTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_add_route_success(self):
        # Отправляем POST запрос с данными маршрута
        response = self.client.post('/add_route/', {'name': 'Test Route'})

        # Проверяем, что ответ успешный и маршрут создан
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)

        # Проверяем, что маршрут был добавлен в базу данных
        route_name = response.json()['route_name']
        self.assertTrue(Place.objects.filter(name=route_name).exists())

    def test_add_route_failure(self):
        # Отправляем POST запрос без данных маршрута
        response = self.client.post('/add_route/')

        # Проверяем, что запрос завершился неудачно
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)

        # Проверяем, что маршрут не был добавлен в базу данных
        self.assertFalse(Place.objects.exists())

  # Импортируем модели City и Model из вашего приложения
##ввести город
class FilterModelsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем несколько городов и моделей для тестов
        self.city1 = City.objects.create(name='City1')
        self.city2 = City.objects.create(name='City2')
        self.model1_city1 = models.objects.create(name='Model1_City1', city=self.city1)
        self.model2_city1 = models.objects.create(name='Model2_City1', city=self.city1)
        self.model1_city2 = models.objects.create(name='Model1_City2', city=self.city2)

    def test_filter_models_success(self):
        # Отправляем POST запрос с названием существующего города
        response = self.client.post('/filter_models/', {'city': 'City1'})

        # Проверяем, что ответ успешный и модели были найдены
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)

        # Проверяем, что в ответе содержатся правильные имена моделей для указанного города
        expected_models = ['Model1_City1', 'Model2_City1']
        self.assertListEqual(response.json()['models'], expected_models)

    def test_filter_models_failure(self):
        # Отправляем POST запрос с названием несуществующего города
        response = self.client.post('/filter_models/', {'city': 'NonExistingCity'})

        # Проверяем, что запрос завершился неудачно и не было найдено моделей
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)
        self.assertNotIn('models', response.json())

  # Импортируем функцию get_coordinates из вашего приложения
##получить местоположение
class GetCoordinatesTestCase(TestCase):
    @patch('myapp.views.get_coordinates')
    def test_get_coordinates(self, mock_get):
        # Мокируем ответ от внешнего API
        mock_response = {
            "response": {
                "GeoObjectCollection": {
                    "featureMember": [
                        {
                            "GeoObject": {
                                "Point": {
                                    "pos": "37.622504 55.753215"
                                }
                            }
                        }
                    ]
                }
            }
        }
        mock_get.return_value.json.return_value = mock_response

        # Вызываем функцию get_coordinates с тестовым аргументом
        coordinates = get_coordinates("Москва")

        # Проверяем, что функция вернула ожидаемые координаты
        self.assertEqual(coordinates, ["37.622504", "55.753215"])
  # Импортируем функцию build_route из вашего приложения
##создать путь для карты
class BuildRouteTestCase(TestCase):
    @patch('myapp.views.requests.get')
    @patch('myapp.views.get_coordinates')
    def test_build_route(self, mock_get_coordinates, mock_get):
        # Мокируем ответ от внешних API
        mock_coordinates = [("37.622504", "55.753215"), ("30.315868", "59.939095")]
        mock_get_coordinates.side_effect = mock_coordinates
        mock_response = {
            # Здесь может быть фиктивный ответ от API
        }
        mock_get.return_value.json.return_value = mock_response

        # Вызываем функцию build_route с тестовыми данными
        places = ["Москва", "Санкт-Петербург"]
        result = build_route(places)

        # Проверяем, что функция вернула ожидаемый результат
        # Тут можно добавить дополнительные проверки в зависимости от ожидаемого формата ответа
        self.assertEqual(result, mock_response)
##визуализировать
class ShowRouteTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('your_app_name.views.build_route')
    def test_show_route_post(self, mock_build_route):
        # Мокируем ответ от функции build_route
        mock_route_data = {'route': 'mocked_data'}
        mock_build_route.return_value = mock_route_data

        # Отправляем POST запрос с данными о местах
        places = ['Москва', 'Санкт-Петербург']
        response = self.client.post('/show_route/', {'places[]': places})

        # Проверяем, что ответ успешный и содержит ожидаемые данные о маршруте
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, mock_route_data)

    def test_show_route_get(self):
        # Отправляем GET запрос
        response = self.client.get('/show_route/')

        # Проверяем, что возвращается ошибка, т.к. метод GET не поддерживается
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'error': 'Метод GET не поддерживается'})

#сохранить маршрут


class SaveFavoriteTransportRouteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('myapp.views.TransportRoute.objects.get')
    @patch('myapp.views.JsonResponse')
    def test_save_favorite_transport_route_success(self, mock_json_response, mock_get):
        # Мокируем вызов TransportRoute.objects.get
        mock_transport_route = TransportRoute(name='TestRoute', departure='CityA', arrival='CityB')
        mock_get.return_value = mock_transport_route

        # Создаем POST запрос с корректными данными
        request = self.factory.post('/save_favorite_transport_route/', {'route_id': 1})

        # Отправляем запрос в функцию save_favorite_transport_route
        response = save_favorite_transport_route(request)

        # Проверяем, что был создан объект FavoriteRoute
        self.assertTrue(FavoriteRoute.objects.filter(name='TestRoute').exists())
        self.assertEqual(response, mock_json_response.return_value)

    @patch('myapp.views.JsonResponse')
    def test_save_favorite_transport_route_invalid_id(self, mock_json_response):
        # Создаем POST запрос с недопустимым route_id
        request = self.factory.post('/save_favorite_transport_route/', {'route_id': 999})

        # Отправляем запрос в функцию save_favorite_transport_route
        response = save_favorite_transport_route(request)

        # Проверяем, что возвращается JSON с сообщением об ошибке
        self.assertEqual(response, mock_json_response.return_value)

#примерная стоимость
class CalculateTripCostTestCase(TestCase):
    def test_calculate_trip_cost(self):
        # Создаем фиктивные данные для теста
        selected_attractions = [1, 2, 3]  # Идентификаторы выбранных достопримечательностей
        selected_hotel = 1  # Идентификатор выбранного отеля
        selected_tickets = [1, 2]  # Идентификаторы выбранных билетов

        # Мокируем вызовы методов для получения данных о достопримечательностях, отеле и билетах
        with patch('myapp.views.Place.objects.filter') as mock_attractions_filter, \
             patch('myapp.views.Hotel.objects.get') as mock_hotel_get, \
             patch('myapp.views.TransportRoute.objects.filter') as mock_tickets_filter:

            # Мокируем возвращаемые значения
            mock_attractions_filter.return_value = [Place(cost=50), Place(cost=100), Place(cost=75)]
            mock_hotel_get.return_value = Hotel(cost_per_night=200)
            mock_tickets_filter.return_value = [TransportRoute(price=150), TransportRoute(price=100)]

            # Вызываем функцию calculate_trip_cost с фиктивными данными
            total_cost = calculate_trip_cost(selected_attractions, selected_hotel, selected_tickets)

            # Проверяем, что общая стоимость рассчитана правильно
            expected_total_cost = 50 + 100 + 75 + 200 + 150 + 100
            self.assertEqual(total_cost, expected_total_cost)
#бронирование отеля
class FilterHotelsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_hotels(self):
        # Создаем GET запрос с параметрами для фильтрации отелей
        request = self.factory.get('/filter_hotels/', {
            'num_people': 2,
            'star_rating': 4,
            'check_in_date': '2024-04-30',
            'check_out_date': '2024-05-01'
        })

        # Мокируем вызовы методов для получения данных о доступных отелях
        with patch('your_app_name.views.Hotel.objects.filter') as mock_hotel_filter:
            # Мокируем возвращаемые значения
            mock_hotel_filter.return_value = [
                Hotel(star_rating=5, available_rooms=3),
                Hotel(star_rating=4, available_rooms=2),
                Hotel(star_rating=3, available_rooms=5)
            ]

            # Вызываем функцию filter_hotels с фиктивными данными
            hotels = filter_hotels(request.GET.get('num_people'), request.GET.get('star_rating'),
                                    request.GET.get('check_in_date'), request.GET.get('check_out_date'))

            # Проверяем, что отели были правильно отфильтрованы
            self.assertEqual(len(hotels), 1)  # Предположим, что только один отель соответствует всем условиям
            self.assertEqual(hotels[0].star_rating, 4)
            self.assertEqual(hotels[0].available_rooms, 2)

#бронирование транспорта
class FilterTransportTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filter_transport(self):
        # Создаем GET запрос с параметрами для фильтрации транспорта
        request = self.factory.get('/filter_transport/', {
            'transport_type': 'train',
            'seats': 50,
            'departure_city': 'CityA',
            'arrival_city': 'CityB',
            'departure_date': '2024-04-30',
            'arrival_date': '2024-05-01'
        })

        # Мокируем вызовы методов для получения данных о транспорте
        with patch('your_app_name.views.TransportRoute.objects.filter') as mock_transport_filter:
            # Мокируем возвращаемые значения
            mock_transport_filter.return_value = [
                TransportRoute(transport_type='train', seats=50, departure_city='CityA', arrival_city='CityB'),
                TransportRoute(transport_type='bus', seats=40, departure_city='CityA', arrival_city='CityB')
            ]

            # Вызываем функцию filter_transport с фиктивными данными
            response = filter_transport(request)

            # Проверяем, что транспорт был правильно отфильтрован
            self.assertEqual(len(response.context_data['transport']), 1)  # Предположим, что только один маршрут соответствует всем условиям
            self.assertEqual(response.context_data['transport'][0].transport_type, 'train')
            self.assertEqual(response.context_data['transport'][0].seats, 50)
            self.assertEqual(response.context_data['transport'][0].departure_city, 'CityA')
            self.assertEqual(response.context_data['transport'][0].arrival_city, 'CityB')

#изменение маршрута
class HandleEditButtonTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_handle_edit_button_sightseeing(self):
        # Создаем GET запрос с действием 'sightseeing'
        request = self.factory.get(reverse('handle_edit_button'), {'action': 'sightseeing'})

        # Вызываем функцию handle_edit_button
        response = handle_edit_button(request, 'sightseeing')

        # Проверяем, что произошло перенаправление на страницу выбора достопримечательностей
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('choose_sightseeing'))

    def test_handle_edit_button_accommodation(self):
        # Создаем GET запрос с действием 'accommodation'
        request = self.factory.get(reverse('handle_edit_button'), {'action': 'accommodation'})

        # Вызываем функцию handle_edit_button
        response = handle_edit_button(request, 'accommodation')

        # Проверяем, что произошло перенаправление на страницу бронирования жилья
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('book_accommodation'))

    def test_handle_edit_button_transport(self):
        # Создаем GET запрос с действием 'transport'
        request = self.factory.get(reverse('handle_edit_button'), {'action': 'transport'})

        # Вызываем функцию handle_edit_button
        response = handle_edit_button(request, 'transport')

        # Проверяем, что произошло перенаправление на страницу бронирования транспорта
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('book_transport'))

    def test_handle_edit_button_invalid_action(self):
        # Создаем GET запрос с некорректным действием
        request = self.factory.get(reverse('handle_edit_button'), {'action': 'invalid'})

        # Вызываем функцию handle_edit_button
        response = handle_edit_button(request, 'invalid')

        # Проверяем, что произошло перенаправление на главную страницу
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('main'))

#перенос данных в pdf
class GeneratePDFTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_generate_pdf(self):
        # Создаем GET запрос
        request = self.factory.get('/generate_pdf/')

        # Вызываем функцию generate_pdf
        response = generate_pdf(request)

        # Проверяем, что ответ содержит PDF-файл
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.get('Content-Type'), 'application/pdf')
        self.assertIn('attachment; filename="favorite_route.pdf"', response.get('Content-Disposition'))

        # Проверяем, что PDF-документ содержит правильную информацию о маршруте
        buffer = BytesIO(response.content)
        pdf = canvas.Canvas(buffer)
        text_content = buffer.getvalue().decode('utf-8')

        # Проверяем наличие информации о маршруте в PDF-документе
        self.assertIn('Избранный маршрут', text_content)
        # Здесь вы можете добавить дополнительные проверки для других данных маршрута

        buffer.close()

#олучение информации о достпримечательностях
class GetLandmarksTestCase(unittest.TestCase):
    @patch('your_app_name.views.requests.get')
    def test_get_landmarks_success(self, mock_requests_get):
        # Устанавливаем мокированный ответ для успешного запроса
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'features': [
                {'properties': {'name': 'Landmark 1'}},
                {'properties': {'name': 'Landmark 2'}}
            ]
        }
        mock_requests_get.return_value = mock_response

        # Вызываем функцию get_landmarks
        landmarks = get_landmarks(55.7558, 37.6176)

        # Проверяем, что функция вернула ожидаемые достопримечательности
        self.assertEqual(len(landmarks), 2)
        self.assertEqual(landmarks[0]['properties']['name'], 'Landmark 1')
        self.assertEqual(landmarks[1]['properties']['name'], 'Landmark 2')

    @patch('your_app_name.views.requests.get')
    def test_get_landmarks_failure(self, mock_requests_get):
        # Устанавливаем мокированный ответ для неуспешного запроса
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        # Вызываем функцию get_landmarks
        landmarks = get_landmarks(55.7558, 37.6176)

        # Проверяем, что функция вернула пустой список в случае ошибки
        self.assertEqual(landmarks, [])


class LandmarksViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_landmarks_view_get(self):
        # Создаем GET запрос к представлению
        request = self.factory.get('/landmarks/')
        response = landmarks_view(request)

        # Проверяем, что представление возвращает правильный шаблон и объект формы
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landmark_form.html')
        self.assertIsInstance(response.context_data['form'], LandmarkForm)

    def test_landmarks_view_post_valid_form(self):
        # Создаем POST запрос с правильными данными формы
        request = self.factory.post('/landmarks/', {'latitude': 55.7558, 'longitude': 37.6176})
        response = landmarks_view(request)

        # Проверяем, что представление возвращает правильный шаблон и данные о достопримечательностях
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landmarks.html')
        self.assertTrue('landmarks' in response.context_data)

    def test_landmarks_view_post_invalid_form(self):
        # Создаем POST запрос с неправильными данными формы
        request = self.factory.post('/landmarks/', {'latitude': 'invalid', 'longitude': 'invalid'})
        response = landmarks_view(request)

        # Проверяем, что представление возвращает форму с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'landmark_form.html')
        self.assertIsInstance(response.context_data['form'], LandmarkForm)
        self.assertTrue(response.context_data['form'].errors)

#получения маршрутов между двумя точками с помощью API Яндекс.Карт
class GetRoutesTestCase(unittest.TestCase):
    @patch('your_app_name.views.requests.get')
    def test_get_routes_success(self, mock_requests_get):
        # Устанавливаем мокированный ответ для успешного запроса
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'routes': [
                {'distance': 100, 'duration': 60},
                {'distance': 150, 'duration': 90}
            ]
        }
        mock_requests_get.return_value = mock_response

        # Вызываем функцию get_routes
        routes = get_routes('origin', 'destination')

        # Проверяем, что функция вернула ожидаемые маршруты
        self.assertEqual(len(routes), 2)
        self.assertEqual(routes[0]['distance'], 100)
        self.assertEqual(routes[0]['duration'], 60)
        self.assertEqual(routes[1]['distance'], 150)
        self.assertEqual(routes[1]['duration'], 90)

    @patch('your_app_name.views.requests.get')
    def test_get_routes_failure(self, mock_requests_get):
        # Устанавливаем мокированный ответ для неуспешного запроса
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        # Вызываем функцию get_routes
        routes = get_routes('origin', 'destination')

        # Проверяем, что функция вернула пустой список в случае ошибки
        self.assertEqual(routes, [])


class RoutesViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_routes_view_post_valid_form(self):
        # Создаем POST запрос с правильными данными формы
        request = self.factory.post('/routes/', {'origin': 'Москва', 'destination': 'Санкт-Петербург'})
        response = routes_view(request)

        # Проверяем, что представление возвращает правильный шаблон и данные о маршрутах
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'routes.html')
        self.assertTrue('routes' in response.context_data)

    def test_routes_view_post_invalid_form(self):
        # Создаем POST запрос с неправильными данными формы
        request = self.factory.post('/routes/', {'origin': '', 'destination': ''})
        response = routes_view(request)

        # Проверяем, что представление возвращает форму с ошибками
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'route_form.html')
        self.assertIsInstance(response.context_data['form'], RouteForm)
        self.assertTrue(response.context_data['form'].errors)

    def test_routes_view_get(self):
        # Создаем GET запрос к представлению
        request = self.factory.get('/routes/')
        response = routes_view(request)

        # Проверяем, что представление возвращает правильный шаблон и объект формы
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'route_form.html')
        self.assertIsInstance(response.context_data['form'], RouteForm)


class GetHotelsTestCase(unittest.TestCase):
    @patch('your_app_name.views.requests.get')
    def test_get_hotels_success(self, mock_requests_get):
        # Устанавливаем мокированный ответ для успешного запроса
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'features': [
                {'properties': {'name': 'Hotel 1', 'address': 'Address 1'}},
                {'properties': {'name': 'Hotel 2', 'address': 'Address 2'}}
            ]
        }
        mock_requests_get.return_value = mock_response

        # Вызываем функцию get_hotels
        hotels = get_hotels(55.7558, 37.6176)

        # Проверяем, что функция вернула ожидаемые гостиницы
        self.assertEqual(len(hotels), 2)
        self.assertEqual(hotels[0]['properties']['name'], 'Hotel 1')
        self.assertEqual(hotels[0]['properties']['address'], 'Address 1')
        self.assertEqual(hotels[1]['properties']['name'], 'Hotel 2')
        self.assertEqual(hotels[1]['properties']['address'], 'Address 2')

    @patch('your_app_name.views.requests.get')
    def test_get_hotels_failure(self, mock_requests_get):
        # Устанавливаем мокированный ответ для неуспешного запроса
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        # Вызываем функцию get_hotels
        hotels = get_hotels(55.7558, 37.6176)

        # Проверяем, что функция вернула пустой список в случае ошибки
        self.assertEqual(hotels, [])

if __name__ == '__main__':
    unittest.main()
