FROM python:3.4

RUN apt-get -y update
RUN apt-get install -y apt-utils software-properties-common vim curl apache2 apache2-utils python3 libapache2-mod-wsgi-py3


RUN mkdir /requirements
WORKDIR /requirements
ADD requirements.txt /requirements

RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt


ADD ./demo_site.conf /etc/apache2/sites-available/000-default.conf
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]