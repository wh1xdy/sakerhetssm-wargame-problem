FROM python:3-slim-bookworm

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENV FLAG=SSM{wow_you_managed_to_access_the_admin_thingy}
EXPOSE 3000

CMD ["python3", "app.py"]