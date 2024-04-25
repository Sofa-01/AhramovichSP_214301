document.addEventListener('DOMContentLoaded', function() {
    // Получаем кнопки по их идентификаторам
    var loginButton = document.getElementById('Button');


    loginButton.addEventListener('click', function() {
        // Перенаправляем пользователя на страницу входа
        window.location.href = '/create/';
    });
});