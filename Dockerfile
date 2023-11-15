FROM python:3.9.18-bullseye

WORKDIR /usr/src

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /usr/src
COPY . /usr/src/
CMD [ "python", "-u", "main.py" ]