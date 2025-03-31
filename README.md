# Foodgram
 Дипломный проект Яндекс Практикум по направлению Python Backend разработчик +.
 Проект представляет из себя веб-приложение, где пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
## Автор
[DenisTereshkov](https://github.com/DenisTereshkov)
## Технологический стек
- Python
- Django
- Django REST Framework
- Gunicorn
- Nginx
- Docker Compose
- GitHub Actions
- PostgreSQL
- SQLite
## CI/CD
- Для корректной работы GitHub Worflow необходимо проводить пуш проекта в ветку main, а также настроить для репозитория следующие секреты:
- DOCKER_LOGIN
- DOCKER PASSWORD
- HOST (IP сервера)
- USER (Имя пользователя на сервере)
- SSH_KEY
- SSH_PHASSPHRASE

### Спецификация API
- Находясь в корневой папке проекта:
```
cd infra
```
```
docker compose up
``` 
При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для фронтенд-приложения, а затем прекратит свою работу. 
По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

## Как развернуть проект на удаленном сервере с помощью Docker:
- Создать на сервере папку для проекта и перейти в нее
```
sudo mkdir foodgram
```
```
cd foodgram
```
- Скопировать файл docker-compose.production.yml и в этой директории создать файл .env по шаблону .env.example

- Создать и запустить контейнеры Docker, выполнить команду на сервере. Выполнить миграции
```
sudo docker compose -f docker-compose.production.yml up -d
```
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
- Наполнить базу данными:
```
sudo docker compose exec foodgram-backend-1 python manage.py import_ingredients_tags
```

- Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic
```
```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

### Локальный запуск без Docker:

- Находясь в корневой папке проекта:
```
touch .env 
```
-заполнить .env по шаблону .env.example
```
cd backend
```
- выполнить команды:
```
python manage.py migrate
```
```
python manage.py import_ingredients_tags
```
```
python manage.py createsuperuser
```
```
python manage.py runserver
```