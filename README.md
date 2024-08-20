Продуктовый помощник - Дипломный проект курса Python-разработчик от Яндекс.Практикум.
Описание проекта:
«Продуктовый помощник» — сайт, на котором можно публиковать рецепты и подписываться на публикации других авторов. Понравившиеся рецепты можно добавить в избранное. Сервис «Список покупок» позволяет скачать список продуктов, которые понадобятся для приготовления выбранных блюд.
Запуск проекта на сервере:
Клонировать репозиторий и перейти в директорию infra:
'''
git clone 
'''
Создать файл .env по шаблону .env.template:
'''
cp .env.template .env
'''
Запустить приложение:
'''
docker-compose up
'''
Провести миграции:
'''
docker-compose exec web python manage.py migrate --noinput
'''
Создать суперпользователя:
'''
docker-compose exec web python manage.py createsuperuser
'''
Импортировать данные в базу данных:
'''
docker-compose exec web python manage.py import_data
'''
Технологии:
Python Django Django REST Framework PostgreSQL Nginx gunicorn docker GitHubActions 