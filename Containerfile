FROM docker.io/library/python:3.10

RUN apt-get update

RUN apt-get install -y cython3

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["python3", "-m", "app.main"]
