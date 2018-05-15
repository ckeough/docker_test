FROM ubuntu:16.04

RUN apt-get -y update
RUN apt-get install -y apt-utils software-properties-common vim curl apache2 apache2-utils python3 libapache2-mod-wsgi-py3 gdal-bin python3-gdal wget

ENV GDAL_VERSION=2.2.4
RUN wget http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz
RUN tar -xzf gdal-${GDAL_VERSION}.tar.gz
RUN cd gdal-${GDAL_VERSION}; ./configure --with-python; make; make install
RUN ldconfig

RUN mkdir /requirements
WORKDIR /requirements
ADD requirements.txt /requirements

RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host pypi.python.org GDAL
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt


ADD ./demo_site.conf /etc/apache2/sites-available/000-default.conf
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]