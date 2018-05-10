FROM ubuntu

RUN apt-get update

RUN apt-get install -y vim
RUN apt-get install -y curl
RUN apt-get install -y apache2
RUN apt-get install -y apache2-utils
RUN apt-get -y install python3 libapache2-mod-wsgi-py3
RUN ln /usr/bin/python3 /usr/bin/python
RUN apt-get -y install python3-pip
RUN ln /usr/bin/pip3 /usr/bin/pip


RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt


ADD ./demo_site.conf /etc/apache2/sites-available/000-default.conf
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]
