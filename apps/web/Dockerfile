FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY app.py /app/app.py
COPY index.html /app/index.html
COPY login.html /app/login.html
COPY private.html /app/private.html

EXPOSE 8000
CMD ["python", "-u", "app.py"]
