FROM python:3.5

RUN apt-get update && \
    apt-get install -y debconf locales && \
    apt-get autoclean && \
    apt-get autoremove && \
    dpkg-reconfigure --frontend noninteractive locales && \
    locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8

RUN mkdir -p /code/bookinglog
WORKDIR /code
ADD requirements.txt /code/
ADD ./bookinglog /code/bookinglog/
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-m", "bookinglog.scrape"]
