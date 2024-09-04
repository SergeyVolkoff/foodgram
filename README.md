### Продуктовый помощник - Дипломный проект курса Python-разработчик от Яндекс.Практикум. Доступен тут https://foodgramic.ddns.net
### Описание проекта:
«Продуктовый помощник» — сайт, на котором можно публиковать рецепты и подписываться на публикации других авторов. Понравившиеся рецепты можно добавить в избранное. Сервис «Список покупок» позволяет скачать список продуктов, которые понадобятся для приготовления выбранных блюд.
### Запуск проекта на сервере:
Клонировать репозиторий и перейти в директорию infra:
'''
git clone https://github.com/SergeyVolkoff/foodgram.git
```
Создать файл .env по шаблону .env.template:
```
cp .env.template .env
```

Установите docker и  docker-compose на сервер:
```
apt install docker.io 
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

```
Запустить приложение:
```
docker-compose up
```
Провести миграции:
```
docker-compose exec web python manage.py migrate --noinput
```
Создать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```

### Технологии:
 Python Django Django REST Framework PostgreSQL Nginx gunicorn docker GitHubActions 
