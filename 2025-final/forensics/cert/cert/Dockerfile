FROM debian:latest
COPY ca_generator /usr/bin/ca_generator
RUN apt update && apt install -y strace
ENTRYPOINT ["bash"]