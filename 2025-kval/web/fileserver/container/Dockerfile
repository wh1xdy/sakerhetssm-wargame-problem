FROM php:apache
COPY index.php .htaccess flag.txt /var/www/html/
RUN chown -R root:root /var/www/html/
RUN a2enmod rewrite
