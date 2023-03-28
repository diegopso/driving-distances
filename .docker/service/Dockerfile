FROM python:3.11

ARG name
ARG uid
ARG gid

RUN addgroup --gid $gid $name && \
    adduser --uid $uid --gid $gid --disabled-password $name

USER $name
WORKDIR /home/$name

COPY ./service/setup.py ./

RUN pip install --upgrade pip && \ 
    pip install .