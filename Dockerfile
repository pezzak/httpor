FROM python:3.5

WORKDIR /opt/app
COPY . /opt/app

RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get -y install zabbix-agent

CMD ["python", "server.py"]
