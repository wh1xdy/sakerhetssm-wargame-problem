FROM python:3.11-slim
WORKDIR /app
COPY smtp_server.py .
RUN pip install aiosmtpd
EXPOSE 1025
CMD ["python", "smtp_server.py"]
