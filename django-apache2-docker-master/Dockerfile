FROM ubuntu:16.04
RUN apt-get -y update
RUN apt-get install -y apt-utils software-properties-common vim curl apache2 apache2-utils python3 libapache2-mod-wsgi-py3 gdal-bin python3-gdal python3-pip

RUN mkdir /requirements
WORKDIR /requirements
ADD requirements.txt /requirements

RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

ADD ./demo_site.conf /etc/apache2/sites-available/000-default.conf
#Allow container port 80 to be exposed to the host on both TCP and UDP
EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]