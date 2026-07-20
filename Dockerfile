FROM python:3.11.0-slim
WORKDIR /app/
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update
COPY requirements.txt .
RUN pip install pip --upgrade
RUN pip install setuptools wheel --upgrade
RUN pip install --no-cache-dir --no-deps -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]