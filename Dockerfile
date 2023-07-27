FROM python:3.10

# Install necessary tools
RUN apt-get update && apt-get install -y wget gnupg2

# Download Google Chrome .deb package from the provided link
RUN wget "https://www.slimjet.com/chrome/download-chrome.php?file=files%2F104.0.5112.102%2Fgoogle-chrome-stable_current_amd64.deb" -O /tmp/google-chrome-stable_current_amd64.deb

# Install the .deb package
RUN apt-get install -y /tmp/google-chrome-stable_current_amd64.deb

# Clean up the downloaded package
RUN rm /tmp/google-chrome-stable_current_amd64.deb


WORKDIR /usr/src/app

#prepare python dependecies
COPY requirements.txt .
RUN  python3 -m pip install --no-cache-dir -r requirements.txt

#copy app files
COPY . .

ENV SERVICE_PORT=80
EXPOSE $SERVICE_PORT

#environemnt variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV COOKIES_FILE_NAME=flask_service/cookies.pkl
# set display port to avoid crash
ENV DISPLAY=:99

CMD /usr/bin/env python flask_service/wine_searcher_service.py