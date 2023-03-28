FROM mysql:5.7-debian

ARG name
ARG uid
ARG gid

RUN addgroup --gid $gid $name && \
    adduser --uid $uid --gid $gid --disabled-password $name