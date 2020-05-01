FROM ubuntu:20.04

# System Requirements
RUN apt-get update -y
RUN apt-get install python3 python3-pip libpq-dev git iptables -y

# VPN Set up
ARG VPN=false
ENV USE_VPN $VPN
WORKDIR /usr/src/vpn
RUN if [ "$VPN" = true ] ; then apt-get install openvpn -y ; else echo Arugment is $vpn ; fi
COPY Dockerfile client.* ./

# App Requirements
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy Application
COPY . .
RUN chmod 744 startup.sh

CMD ./startup.sh "$USE_VPN"