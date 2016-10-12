FROM ubuntu

RUN apt-get update && \
    apt-get install -y python3 \
                       python-dev \
                       python-pip && \
    rm -rf /var/lib/apt/lists/*

VOLUME ["/tmp/data/down-resource"]

ADD . /down-resource
