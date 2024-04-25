document.addEventListener('DOMContentLoaded', function() {
    // Получаем кнопки по их идентификаторам
    var loginButton = document.getElementById('signinButton');
    var signupButton = document.getElementById('signupButton');

    // Добавляем обработчик клика на кнопку Вход
    loginButton.addEventListener('click', function() {
        // Перенаправляем пользователя на страницу входа
        window.location.href = '/signin/';
    });

    // Добавляем обработчик клика на кнопку Регистрация
    signupButton.addEventListener('click', function() {
        // Перенаправляем пользователя на страницу регистрации
        window.location.href = '/signup/';
    });
});
