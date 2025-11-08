FROM php:7.2-apache

COPY index.php /var/www/html/
COPY c99.php /var/www/html/
COPY image.png /var/www/html/
COPY flag.txt /

RUN chown -R root:root /var/www/html/
RUN chmod -R 555 /var/www/html/

RUN adduser ctf

USER ctf
