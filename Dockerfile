FROM python:3.9.5
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN rm -rf requirements.txt
EXPOSE 8001