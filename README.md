<h2 align="center">Проект на Django<a href="https://daniilshat.ru/" target="_blank"> - Календарь</a></h2>

___Веб-приложение, предназначенное для создания целей и управления ими, а также для обмена ими с другими пользователями___

>Используемый стек:
>- python3.9
>- Django
>- Postgres

ЗАПУСК:
1. Клонировать проект, создать виртуальное окружение.
2. Выполнить pip install -r requirements.txt
3. Создать в корне проекта файл ".env" и прописать в нем параметры:
   - DEBUG=False
   - SECRET_KEY=Секретный ключ Django
   - POSTGRES_DB=название БД
   - POSTGRES_USER=имя пользователя БД
   - POSTGRES_PASSWORD=пароль для подключения к БД
   - POSTGRES_HOST=хост размещения БД
   - AUTH_KEY=идентификационный ключ от ВК
   - AUTH_SECRET=секретный ключ от ВК
   - TOKEN_BOT=токен телеграмм-бота

4. Создать базу данных: 
 - docker-compose up -d

5. Создать и применить миграции:
➡ python todolist/manage.py makemigrations
➡➡ python todolist/manage.py migrate

6. Создать суперпользователя для входа в админ панель:
➡➡  python todolist/manage.py createsuperuser

7. Запустить проект:
➡  python todolist/manage.py runserver


