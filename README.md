# Запуск системы

### 1. Установите Docker Desktop

(если он еще не установлен)

Docker compose входит в его состав

### 2. Клонируйте репозиторий в любую папку на локальном диске диск

Это можно сделать с помощью GitHub Desktop, или просто скачать zip файл репозитория и разархивировать

### 3. Запустите docker-compose.yml

В командной строке Windows или терминале Mac OS / Linux, перейдите в папку репозитория с помощью `cd C:\Projects\newins_repository` или `cd ~/Documents/GitHub/newins_repository` соответственно, заменив путь на тот, куда Вы клонировали репозиторий, а затем выполните команду:

```docker compose up```

# Проверка, что все работает

В базе данных tender_data на сервере Postgres host.docker.internal:5431, к которой можно подключиться с помощью **DBeaver** или любой другой программы (user `postgres`, пароль `_StrongPass1`), в таблице `tenders`, должны начать появляться новые записи с информацией о тендерах - записи, соответствующие запросам в таблице `request` - т.е для каждой комбинации регион-отрасль, которую добавили в эту таблицу. По умолчанию в ней всего 2 запроса, но при необходимости можно добавить больше, и данные будут сохранены при следующем запуске. По умолчанию там добавлены: 1) строительство и реконструкция зданий - город Москва и 2) строительство и реконструкция зданий - Московская область