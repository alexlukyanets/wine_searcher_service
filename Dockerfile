FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV COOKIES_FILE_NAME=flask_service/cookies.pkl

ARG PROXY
ENV PROXY=$PROXY
ARG CHANGE_IP_URL
ENV CHANGE_IP_URL=$CHANGE_IP_URL

WORKDIR /usr/src/app
COPY . /usr/src/app

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

RUN pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python", "flask_service/wine_searcher_service.py"]