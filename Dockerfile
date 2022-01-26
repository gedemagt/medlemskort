FROM python:3.8-alpine

RUN apk add zlib-dev jpeg-dev gcc musl-dev
RUN pip3 install qrcode[pil] flask flask-login gunicorn

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]