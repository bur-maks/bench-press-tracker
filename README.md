# Bench Press Tracker



A web application for tracking bench press results, monitoring progress and comparing results through leaderboards.



I created this project during the summer after completing my first year at university.  

It was made as a personal practice project to improve my skills in Python, backend development, databases and web development.



## Features



- User registration and login

- JWT authentication

- Password hashing with bcrypt

- Personal user profile

- Bench press result tracking

- Estimated 1RM calculation

- Progress chart

- Absolute leaderboard

- Relative leaderboard

- Profile editing

- SQLite database



## Technologies



- Python

- FastAPI

- SQLAlchemy

- SQLite

- JWT

- bcrypt

- HTML

- CSS

- JavaScript

- Chart.js



## Project structure



```text

bench-press-tracker/

├── static/

│   └── index_fixed.html

├── .env.example

├── .gitignore

├── main.py

├── requirements.txt

├── bench_site.pyproj

└── bench_site.sln

```



## Installation



Clone the repository:



```bash

git clone https://github.com/bur-maks/bench-press-tracker.git

cd bench-press-tracker

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Create a `.env` file based on `.env.example`:



```env

SECRET_KEY=your_secret_key_here

```



Run the application:



```bash

python main.py

```



Open in the browser:



```text

http://127.0.0.1:8000/

```



## Database



The application currently uses SQLite.



The database file is intentionally excluded from the repository because it can contain user data.



If the database does not exist, the application automatically creates a new one when it starts.



## Security



- Passwords are stored as bcrypt hashes

- Authentication uses JWT tokens

- Secret keys are stored in environment variables

- `.env` and database files are excluded from Git



## Project status



The local version of the application is working.



Planned improvements:



- Public deployment

- Production database configuration

- HTTPS

- Improved authentication and session handling

- Additional statistics

- UI improvements



## Author



Maxim Burmatov  

Computer Science and Computer Engineering student at INRTU.



---



# Bench Press Tracker — Русская версия



Веб-приложение для отслеживания результатов в жиме лёжа, просмотра прогресса и сравнения результатов пользователей через рейтинги.



Я сделал этот проект летом после окончания первого курса университета.  

Он создавался как личный учебный проект для практики Python, backend-разработки, работы с базами данных и веб-разработки.



## Возможности



- Регистрация пользователей и вход в аккаунт

- JWT-аутентификация

- Хеширование паролей с помощью bcrypt

- Личный профиль пользователя

- Сохранение результатов жима лёжа

- Расчёт примерного 1RM

- График прогресса

- Абсолютный рейтинг

- Относительный рейтинг

- Редактирование профиля

- База данных SQLite



## Используемые технологии



- Python

- FastAPI

- SQLAlchemy

- SQLite

- JWT

- bcrypt

- HTML

- CSS

- JavaScript

- Chart.js



## Структура проекта



```text

bench-press-tracker/

├── static/

│   └── index_fixed.html

├── .env.example

├── .gitignore

├── main.py

├── requirements.txt

├── bench_site.pyproj

└── bench_site.sln

```



## Запуск проекта



Клонировать репозиторий:



```bash

git clone https://github.com/bur-maks/bench-press-tracker.git

cd bench-press-tracker

```



Установить зависимости:



```bash

pip install -r requirements.txt

```



Создать файл `.env` на основе `.env.example`:



```env

SECRET_KEY=your_secret_key_here

```



Запустить приложение:



```bash

python main.py

```



Открыть в браузере:



```text

http://127.0.0.1:8000/

```



## База данных



Сейчас приложение использует SQLite.



Файл базы данных намеренно исключён из репозитория, так как он может содержать данные пользователей.



Если базы данных нет, приложение автоматически создаст новую при запуске.



## Безопасность



- Пароли хранятся в виде bcrypt-хешей

- Для авторизации используются JWT-токены

- Секретный ключ хранится в переменных окружения

- `.env` и файлы базы данных исключены из Git



## Статус проекта



Локальная версия приложения работает.



В дальнейшем планируется:



- Публичное размещение сайта

- Настройка базы данных для публичной версии

- HTTPS

- Улучшение системы авторизации и сессий

- Дополнительная статистика

- Улучшение интерфейса



## Автор



Максим Бурматов  

Студент направления «Информатика и вычислительная техника» ИРНИТУ.

