FROM ubuntu

RUN apt-get update



RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt


ADD ./demo_site.conf /etc/apache2/sites-available/000-default.conf
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]
