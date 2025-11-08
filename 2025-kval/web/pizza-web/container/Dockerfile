FROM tomcat:jre21-temurin-noble

COPY pizzaorder /usr/local/tomcat/webapps/pizza_order
COPY root /usr/local/tomcat/webapps/ROOT
COPY data/flag.txt /flag.txt

EXPOSE 8080
CMD ["catalina.sh", "run"]
