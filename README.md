# Foodgram - это удобный онлайн-сервис для обмена рецептами. Функционал сервиса позволяет после регистрации пользователя создавать свои рецепты, добавлять в избранное чужие рецепты, подписываться на других пользователей, а так же скачивать список покупок с ингредиентами для каждого рецепта.

http://tsk.hopto.org/

## Функционал сервиса

После регистрации на сайте у вас есть возможность:

- Добавлять, редактировать и удалять рецепты с возможностью публикации фотографии блюда;
- Просматривать чужие рецепты, добавлять их в Избранное для быстрого доступа к ним в дальнейшем;
- Подписываться на профили других пользователей, чтобы следить за публикацией новых рецептов;
- Скачивать список покупок необходимых для воспроизведения выбранного рецепта.

## Подготовка к запуску

На сервере создайте папку проекта - foodgram и скопируйте в нее файлы docker-compose.production.yml :

В папке с проектом создайте файл `.env` и заполните его своими данными:

`POSTGRES_USER` - имя пользователя для доступа к базе данных

`POSTGRES_PASSWORD` - пароль для доступа к базе данных

`POSTGRES_DB` - имя базы данных

`SECRET_KEY` - секретный ключ для Django

`DEBUG` - True/False - режим отладки Django

`ALLOWED_HOSTS` - список разрешенных хостов

`DB_HOST` - имя хоста базы данных

`DB_PORT` - порт базы данных

## Запуск проекта

Находясь в папке с проектом скачайте образы и запустите проект командами:
```
sudo docker compose -f docker-compose.production.yml up -d
```

Выполните миграции, соберите статические файлы бэкенда:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
```
sudo docker compose -f docker-compose.production.yml exec backend mkdir -p backend_static/static/
```
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

Создайте суперпользователя:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```