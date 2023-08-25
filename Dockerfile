ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bullseye

LABEL authors="Tema"

WORKDIR /Happy.do_global

COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .
RUN mkdir -p /usr/share/fonts/truetype/ && \
    install -m644 Fonts/* /usr/share/fonts/truetype/

EXPOSE 8080

CMD ["python", "bot.py"]
