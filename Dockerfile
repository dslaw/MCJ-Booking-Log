FROM python:3

RUN apt-get update && \
    apt-get install -y debconf locales && \
    apt-get clean && \
    apt-get autoremove && \
    dpkg-reconfigure --frontend noninteractive locales && \
    locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 -O  phantomjs.tar.bz2 && \
    tar -xjf phantomjs.tar.bz2 && \
    mv phantomjs-*/bin/phantomjs /usr/bin/ && \
    rm -rf phantomjs*

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt && \
    python setup.py install
