FROM mariadb:10.11

ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=news_db
ENV MYSQL_USER=news_user
ENV MYSQL_PASSWORD=news_password

COPY init.sql /docker-entrypoint-initdb.d/init.sql

RUN chmod +r /docker-entrypoint-initdb.d/init.sql

EXPOSE 3306
