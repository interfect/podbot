FROM ubuntu:18.04

RUN DEBIAN_FRONTEND=noninteractive apt-get -q -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get -q -y install \
        python3 \
        python3-pip \
        vlc-bin \
        vlc-data && \
    DEBIAN_FRONTEND=noninteractive apt-get -q -y clean

WORKDIR /podbot
ADD requirements.txt /podbot/requirements.txt
RUN pip3 install -r requirements.txt

ADD podbot.py /podbot/podbot.py

CMD python3 podbot.py

# For usage, mount a podbot.conf as /podbot/podbot.conf
# Make sure to run with --device /dev/snd to enable sound


