FROM python:3.6-alpine
MAINTAINER qytz <hhhhhf@foxmail.com>
LABEL version="0.1.1" description="fintie dev environment based on latest python3"
ENV PS1="\[\e[0;33m\]|> fintie <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

WORKDIR /usr/src/fintie
COPY . .
RUN apk add --update --no-cache --virtual .build-deps musl-dev alpine-sdk git python3-dev && \
    pip install --no-cache-dir pipenv && \
    pip install --no-cache-dir -r requirements.txt && python setup.py install && \
    apk del .build-deps
RUN apk add --no-cache bash gawk sed grep bc coreutils vim
ENV SHELL /bin/bash
RUN addgroup -g 1000 fintie && adduser -D -G fintie -h /fintie -u 1000 fintie
WORKDIR /fintie
USER fintie
# RUN chown fintie:fintie -R .fintie
ENTRYPOINT ["bash"]
