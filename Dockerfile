ARG PYTHON_VERSION=3.10-slim-buster


FROM python:${PYTHON_VERSION}

ARG ALLOWED_HOSTS
ARG CSRF_TRUSTED_ORIGINS	
ARG DATABASE_URL	
ARG DEBUG
ARG EMAIL_HOST_PASSWORD
ARG EMAIL_HOST_USER
ARG SECRET_KEY
# RUN --mount=type=secret,ALLOWED_HOSTS=ALLOWED_HOSTS
ENV ALLOWED_HOSTS $ALLOWED_HOSTS
ENV CSRF_TRUSTED_ORIGINS $CSRF_TRUSTED_ORIGINS
ENV DATABASE_URL $DATABASE_URL	
ENV DEBUG $DEBUG
ENV EMAIL_HOST_PASSWORD $EMAIL_HOST_PASSWORD
ENV EMAIL_HOST_USER $EMAIL_HOST_USER
ENV SECRET_KEY $EMAIL_HOST_USER
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /code/


RUN python manage.py collectstatic --noinput

EXPOSE 8000

# replace demo.wsgi with <project_name>.wsgi
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "myFinance.wsgi"]