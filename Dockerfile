FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
ENTRYPOINT ["python", "flask_service/wine_searcher_service.py"]