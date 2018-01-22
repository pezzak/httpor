# HTTPor - web monitoring tool.

Sometimes you have lots of web resources (maybe pet-projects or something else) and you must be sure that they work. Maintaining tools such as zabbix too expensive. Or you have zabbix, but setup built-in web monitoring looks too complicated.

This app:

- check web resources for expected test string
- check web resources for expected status code
- in case of problem notify in supported services (slack, telegram)
- notify about recovery
- can send information to zabbix via zabbix_sender

## <a name="usage"></a> Usage

1. Prepare config.json:
```
{
    # Proxy (optional)
    "proxy": "http://10.10.10.10:3128",

    # Request timeout
    "timeout": 10,

    # Resources request frequency
    "frequency": 15,

    # Fail threshold
    "trigger_threshold": 2,

    # Recover threshold
    "recover_threshold": 3,

    # Repeat alarm every seconds
    "alarm_repeat": 600,

    # Notification services
    "services": {
      "zabbix": {
        "server": "127.0.0.1",

        #Zabbix sender binary (optional)
        "sender": "/usr/bin/zabbix_sender",

        #Host with linked template
        "host": "superserver.ru"
      },
      "slack": {
        "hook": "https://hooks.slack.com/services/token"
      },
      "telegram": {
        "token": "token",
        "chat_id": "chat_id"
      }
    },
    "resources": {
      "https://www.yandex.ru": {
        "type": "GET",
        "url": "https://www.yandex.ru",
        "expected_text": "Яндекс",
        "expected_code": 200,
        "use_proxy": true
      },
      "https://www.mail.ru": {
        "type": "GET",
        "url": "https://www.mail.ru",
        "expected_text": "Почта Mail.Ru",
        "expected_code": 200,
        "use_proxy": false
      },
      "https://yahoo.co.jp": {
        "type": "POST",
        "url": "https://yahoo.co.jp",
        "expected_text": "メールアドレスを取得",
        "expected_code": 200,
        "data": "login=111",
        "use_proxy": false
      }
    }
}
```
2. Edit path in docker-compose to config.json
```
version: '2'
services:
  httpor:
    image: "pezzak/httpor:latest"
    volumes:
      - "/PATH/TO/CONFIG/config.json:/opt/app/config.json"
    restart: "always"
    network_mode: "host"
```

3. Start app
```
docker-compose run -d
```

4. Enjoy!
