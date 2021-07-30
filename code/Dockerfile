FROM pytorch/pytorch
COPY . /code
WORKDIR /code

RUN apt-get update 
RUN apt-get -y install libpq-dev gcc

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000
CMD flask run --host=0.0.0.0