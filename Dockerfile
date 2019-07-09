FROM python:2

ADD . /MOMFER

WORKDIR /MOMFER

RUN pip install -r requirements.txt
RUN python indexer.py

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]