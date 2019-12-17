FROM atomcream/python3.6.5u

WORKDIR /web

COPY requirements.txt /requirements.txt

RUN pip install -U pip; pip install -r /requirements.txt
