FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# Collect static files
RUN mkdir -p /app/static
RUN python manage.py collectstatic --noinput

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["gunicorn", "recipe_project.wsgi:application", "--bind", "0.0.0.0:8000"]