document.addEventListener('DOMContentLoaded', function() {
    // Получаем кнопки по их идентификаторам
    var hotelButton = document.getElementById('hotel');
    var transButton = document.getElementById('trans');
    var favButton = document.getElementById('fav');

    hotelButton.addEventListener('click', function() {

        window.location.href = '/hotelreserv/';
    });

    // Добавляем обработчик клика на кнопку Регистрация
    transButton.addEventListener('click', function() {
        window.location.href = '/transreserv/';
    });

    favButton.addEventListener('click', function() {
        window.location.href = '/favorite/';
    });
});