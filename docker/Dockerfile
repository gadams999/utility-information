FROM python:3.8.2-slim-buster

RUN apt-get update && apt-get install -yq \
    wget \
    firefox-esr \
    chromium \
    xvfb \
    unzip

# GeckoDriver v0.26.0
RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz" -O /tmp/geckodriver.tgz \
    && tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz

# chromeDriver v80.0.3987.106
RUN wget -q "https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
    && rm /tmp/chromedriver.zip

# xvfb - X server display
ADD xvfb-chromium /usr/bin/xvfb-chromium
RUN ln -s /usr/bin/xvfb-chromium /usr/bin/google-chrome \
    && chmod 777 /usr/bin/xvfb-chromium

# create symlinks to chromedriver and geckodriver (to the PATH)
RUN ln -s /usr/bin/geckodriver /usr/bin/chromium-browser \
    && chmod 777 /usr/bin/geckodriver \
    && chmod 777 /usr/bin/chromium-browser

COPY .united-power.py .
COPY ./requirements/prod.txt .

RUN pip install -r prod.txt

CMD [ "python", "./united-power.py"]
