FROM python:3.11-slim

LABEL authors="Tema"

WORKDIR /Happy.do_global

COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8080

CMD ["python", "bot.py"]
