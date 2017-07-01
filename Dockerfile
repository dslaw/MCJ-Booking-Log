FROM python:3

RUN apt-get update && \
    apt-get install -y debconf locales && \
    apt-get clean && \
    apt-get autoremove && \
    dpkg-reconfigure --frontend noninteractive locales && \
    locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt && \
    python setup.py install
