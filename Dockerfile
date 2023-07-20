FROM python:3.10

# install google chrome and other dependencies
RUN (wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -) \
    && echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get -y update \
    && apt-get install -y --no-install-recommends \
        google-chrome-stable \
        unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

WORKDIR /usr/src/app

#prepare python dependecies
COPY requirements.txt .
RUN  python3 -m pip install --no-cache-dir -r requirements.txt

#copy app files
COPY . .

EXPOSE 5000

#environemnt variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV COOKIES_FILE_NAME=flask_service/cookies.pkl
# set display port to avoid crash
ENV DISPLAY=:99

CMD ./flask_service/wine_searcher_service.py