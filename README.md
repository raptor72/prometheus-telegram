# prometheus-telegram

**prometheus-telegram** - бот для расширения возможностей системы Prometheus по оповещению пользователей о наступлении аварийных событий.

Бот выполняет две задачи:

1. Присылает оповещения об аварийных сообщениях из Prometheus пользователям в Telegram.

2. Так как зачастую в качестве дашборда к Prometheus настраивается Grafana, 
бот дает возможность пользователю загружать скриншоты конкретных графиков из Grafana. 
Это позволяет удаленно получить визуализацию интересующих метрик.

Для работы бота предполагается наличие сконфигурированного Alertmanager:

```yml
receivers:
  - name: 'tlg-bot'
    webhook_configs:
      - url: 'http://127.0.0.1:8080/'
        send_resolved: true
```

Бот настраивается конфигурационным файлом, который указан в main.py:

     DEFAULT_CONFIG = './default_config'

Данный файл не добавлен в репозиторий, поскольку содержит реальные значения ключей и токенов. 
Вместо него в качестве пример присутствует **exhample_config**. 
Перед запуском бота необходимо составить корректный конфигурационный файл и прописать его в main.py
В конфигурационном файле задаются следующие параметры:

**apihelper_proxy** - прокси для Telegram

**grafana_token** - токен для доступа к Grafana

**grafana_url** - адрес веб-нитерфейса Grafana

**bot_token** - токен Telegram бота

**user_list** - список id пользователей Telegram которым будут приходить оповещения от бота

## Использование.

Для запуска необходимо выполнить:

    ./main.py

При этом по умолчанию бот будет прослушивать пор 8080 на поступающие нотификации от Alertmanager. 
Если Alertmanager сконфигурирован на отправку алармов на другой порт необходимо использовать ключ -p с указанием целевого порта.
Например:

    ./main.py -p 5000
    
Для получения оповещений пользователю не требуется выполнение каких либо действий. 
Бот будет присылать пользователю уникальные оповещения, сгенерированые Alertmanager.

Пример оповещения:

