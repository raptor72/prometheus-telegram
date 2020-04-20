FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./* /app/

RUN adduser -D user
RUN chown -R user:user /app/
USER user

EXPOSE 8080
EXPOSE 3000
CMD ["python", "/app/main.py", "-H", "172.17.0.2"]

