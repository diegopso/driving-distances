FROM python:3.11

ARG name
ENV name $name
ARG uid
ENV uid $uid
ARG gid
ENV gid $gid

RUN addgroup --gid $gid $name && \
    adduser --uid $uid --gid $gid --disabled-password $name

USER $name
WORKDIR /home/$name

COPY ./job/setup.py ./

RUN pip install --upgrade pip && \ 
    pip install .