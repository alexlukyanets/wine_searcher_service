FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . .
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python", "wine_searcher_service.py"]