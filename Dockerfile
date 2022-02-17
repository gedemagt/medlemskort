FROM python:3.8-alpine

RUN apk add zlib-dev jpeg-dev gcc musl-dev

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]