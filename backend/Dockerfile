FROM python:3.9
WORKDIR /app
RUN pip install gunicorn==20.1.0
RUN pip install --upgrade pip
COPY requirements.txt .
RUN apt-get update && apt-get upgrade -y
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
