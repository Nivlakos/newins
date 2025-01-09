FROM python:3.12

ENV APP_HOME /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY app/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR $APP_HOME

COPY ./app $APP_HOME

CMD ["python3", "main.py"]
