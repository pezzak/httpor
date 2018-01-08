FROM python:3.6

WORKDIR /opt/app
COPY . /opt/app

RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get -y install zabbix-agent

CMD ["python", "-m", "httpor.server"]
