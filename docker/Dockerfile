FROM python:3.8.2-slim-buster

ADD source/united-power.py
ADD source/requirements/prod.txt

RUN pip install -r prod.txt

CMD [ "python", "./united-power.py"]
