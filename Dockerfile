FROM ubuntu:20.04

# System Requirements
RUN apt-get update -y
RUN apt-get install python3 python3-pip libpq-dev git -y

# App Requirements
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Application
COPY . .
RUN chmod 744 startup.sh

CMD ./startup.sh