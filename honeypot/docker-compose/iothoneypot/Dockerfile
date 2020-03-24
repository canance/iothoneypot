# Source: https://github.com/lobobinario/docker-firmadyne/blob/master/Dockerfile
FROM ubuntu:xenial

WORKDIR /root

#Update
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get upgrade -y

#Initial setup (Based on https://github.com/firmadyne/firmadyne)

RUN apt-get install -y sudo wget python python-pip python-lzma busybox-static fakeroot git kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan p7zip-full iputils-ping vim postgresql && \
    git clone --recursive https://github.com/firmadyne/firmadyne.git

#Setup Extractor
RUN	apt-get install -y git-core wget build-essential liblzma-dev liblzo2-dev zlib1g-dev unrar-free && \
    pip install -U pip

RUN git clone https://github.com/firmadyne/sasquatch && \
    cd sasquatch && \
    make && \
    make install && \
    cd .. && \
    rm -rf sasquatch

RUN git clone https://github.com/devttys0/binwalk.git && \
	cd binwalk && \
	./deps.sh --yes && \
	python ./setup.py install && \
	pip install git+https://github.com/ahupp/python-magic && \
	pip install git+https://github.com/sviehb/jefferson && \
	cd .. && \
	rm -rf binwalk

RUN	apt-get install -y qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils vim

# Setup firmadyne binaries
RUN	cd ./firmadyne && ./download.sh && \
	sed -i  's/#FIRMWARE_DIR=\/home\/vagrant\/firmadyne/FIRMWARE_DIR=\/root\/firmadyne/g' firmadyne.config

# Fix scripts to not specify 127.0.0.1 as postgres host, instead rely on env varables or fallback to localhost
WORKDIR /root/firmadyne/scripts
RUN for script in `ls`; do sed -i 's/-h 127.0.0.1//g' $script; done;
RUN sed -i 's/, host="127.0.0.1"//' tar2db.py

# Fix binwalk package syntax error
RUN sed -i 's/is Not None:/is not None:/' /usr/local/lib/python2.7/dist-packages/binwalk/core/settings.py

# Upgrade qemu to 2.6.0
WORKDIR /root
RUN wget https://download.qemu.org/qemu-2.6.0.tar.xz
RUN tar xvf qemu-2.6.0.tar.xz
WORKDIR /root/qemu-2.6.0
RUN sed -i 's/# deb-src/deb-src/g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get build-dep -y qemu
RUN ./configure --target-list=arm-softmmu
RUN make -j4
RUN make install
ENV PATH=/root/qemu-2.6.0/arm-softmmu:$PATH
RUN apt-get update
RUN apt-get install -y qemu-system-arm tcpdump file git python python-pip vim python-virtualenv lib32ncurses5-dev socat

# Volatility
RUN cd /root && git clone https://github.com/volatilityfoundation/volatility.git
RUN cd /root/volatility && python setup.py install
RUN pip install distorm3

RUN apt-get update
RUN apt-get install -y python-scapy kpartx
RUN python3 -m pip install qmp yapsy scapy python-logstash

ENV PATH=/iothoneypot/scripts:$PATH
RUN apt-get update
# Setup suricata
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:oisf/suricata-stable
RUN apt-get update
RUN apt-get install -y suricata
RUN pip install suricata-update
RUN suricata-update


# Setup filebeat
WORKDIR /root
RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.3.1-amd64.deb
RUN dpkg -i filebeat-7.3.1-amd64.deb
ADD filebeat/filebeat.yml /etc/filebeat/filebeat.yml
RUN chmod go-w /etc/filebeat/filebeat.yml
RUN filebeat modules enable suricata
RUN filebeat setup || true

# pygtail
RUN python3 -m pip install Pygtail

# iptables
RUN apt install -y iptables


ENV DEBIAN_FRONTEND=readline
WORKDIR /iothoneypot
