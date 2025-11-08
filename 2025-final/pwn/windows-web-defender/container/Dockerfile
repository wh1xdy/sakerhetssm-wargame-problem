FROM httpd:2.4

RUN apt-get update && apt-get install -y build-essential libtool libapr1-dev libaprutil1-dev

COPY vuln_module.c /usr/local/apache2/
WORKDIR /usr/local/apache2
RUN apxs -i -a -c vuln_module.c

COPY httpd.conf /usr/local/apache2/conf/
COPY index.html /usr/local/apache2/htdocs/
COPY style.css /usr/local/apache2/htdocs/
COPY style.css /usr/local/apache2/htdocs/
COPY background.jpg /usr/local/apache2/htdocs/
COPY cool_picture1.png /usr/local/apache2/htdocs/
COPY cool_picture2.png /usr/local/apache2/htdocs/
COPY cool_picture3.png /usr/local/apache2/htdocs/
COPY cool_picture4.png /usr/local/apache2/htdocs/
COPY flag.txt /

HEALTHCHECK --start-period=20s --start-interval=1s CMD curl -f http://localhost/ || exit 1