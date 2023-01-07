FROM python:3.9

ENV PYTHONUNBUFFERED = 1

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8887

CMD ["python", "manage.py", "runserver", "0.0.0.0:8887"]