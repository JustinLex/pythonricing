FROM docker.io/library/python:3.10-alpine AS builder
RUN apk add gcc libc-dev make
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY run.py /code/run.py
COPY ./app /code/app
RUN pyinstaller -F -s \
    run.py

FROM alpine AS runner
WORKDIR /code
COPY --from=builder /code/dist /code
CMD ["/code/run"]
