# prometheus-telegram

**prometheus-telegram** - бот для расширения возможностей системы Prometheus по оповещению пользователей о наступлении аварийных событий.

Бот выполняет две задачи:

1. Присылает оповещения об аварийных сообщениях из Prometheus пользователям в Telegram.

2. Так как зачастую в качестве дашборда к Prometheus настраивается Grafana, 
бот дает возможность пользователю загружать скриншоты конкретных графиков из Grafana. 
Это позволяет удаленно получить визуализацию интересующих метрик.

## Требования

Операционная система Linux (работоспособность проверялась на CentOS и Ubuntu)

Python3

Установленные модули из файла requirements.txt

Наличие сконфигурированного Alertmanager:

```yml
receivers:
  - name: 'tlg-bot'
    webhook_configs:
      - url: 'http://127.0.0.1:8080/'
        send_resolved: true
```

Бот настраивается конфигурационным файлом, который указан в main.py:

     DEFAULT_CONFIG = './default_config'

default_config не добавлен в репозиторий, поскольку содержит реальные значения ключей и токенов. 
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
    

По умолчанию прослушивание сообщений от Alertmanager запускается на адресе 127.0.0.1. Если требуется указать иной адрес, используйте опцию -H. Например:

    ./main.py -H 172.17.0.2

Для получения оповещений пользователю не требуется выполнение каких либо действий. 
Бот будет присылать пользователю уникальные оповещения, сгенерированые Alertmanager.

Пример оповещения:

![alt text](images/notification.PNG)

Для начала работы с функционалом загрузки скриншотов из Grafana пользователю необходимо отправить боту команду **/start**.
При этом бот, по сконфигурированному **grafana_url** получит список дашбордов и выведет их в качестве клавиатуры.

Пример начала взаимодействия:

![alt text](images/start.PNG)

Далее необходимо напечатать или выбрать на клавиатуре интересующий дашборд.

Пример выбора дашборда:

![alt text](images/choice_dashboard.PNG)

Бот соберет все графики имиеся на конкретном дашборде и выведет их списком. Из списка необходимо ввыбрать конкретный график.

Пример выбора графика:

![alt text](images/choice_panel.PNG)

Для возврата к списку дашбордов нужно использовать кнопку **go back** 

Пример вызврата к списку дашбордов:

![alt text](images/go_back.PNG)

При вводе несуществующего имени дашборда или несуществующего графика будет получено сообщение об ошибке.

Пример запроса несуществующего графика:

![alt text](images/wrong_message.PNG)


При каких либо изменениях  в дашбордах и графиках необходимо перезапустить бота, чтобы он обновил данную информацию.

## Контейнеризация

Для сборки используйте команду:

     docker build -t your_tag/prometheus-telegram ./

Для запуска контейнера в интрактивном режиме спользуйте:

    docker run -it -p 127.0.0.1:8080:8080 -p 127.0.0.1:3001:3000 your_tag/prometheus-telegram
