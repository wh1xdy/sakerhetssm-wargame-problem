FROM python:3.12-alpine

RUN pip install requests

COPY solve.py .

ENTRYPOINT ["python", "solve.py"]