FROM python:3.7-buster

WORKDIR /usr/src/app/

RUN pip install --upgrade pip
ADD requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

ADD ./ /usr/src/app

CMD ["python", "main.py"]