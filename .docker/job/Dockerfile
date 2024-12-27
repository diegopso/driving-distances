FROM python:3.10.16-slim as builder

ARG PIP_ROOT_USER_ACTION=ignore
ARG PIP_DISABLE_PIP_VERSION_CHECK=1
ARG PIP_NO_CACHE_DIR=1

COPY ./ddmc /ddmc

WORKDIR /ddmc

RUN pip install --upgrade pip poetry && \
    poetry export --without-hashes --format requirements.txt >> requirements.txt && \
    echo 'ddmc @ file:///ddmc ; python_version >= "3.10" and python_version < "4.0"' >> requirements.txt && \
    python -m venv venv && \
    venv/bin/pip3 install -r requirements.txt && \
    venv/bin/pip3 uninstall -y pip

FROM python:3.10.16-slim as final

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONOPTIMIZE=2

ARG ROOTLESS_USER=monty

RUN apt-get update

COPY --from=builder /ddmc/venv /ddmc/venv

RUN echo "${ROOTLESS_USER}:x:1000:${ROOTLESS_USER}" >> /etc/group && \
    echo "${ROOTLESS_USER}:x:1001:" >> /etc/group && \
    echo "${ROOTLESS_USER}:x:1000:1001::/workdir:" >> /etc/passwd && \
    mkdir -p /workdir && \
    chmod -R 775 /workdir && \
    chown -R ${ROOTLESS_USER}:${ROOTLESS_USER} /workdir && \
    rm -rf /bin /usr/bin /usr/local/bin

    
COPY --from=builder /usr/local/bin/python /usr/local/bin/python
    
USER ${ROOTLESS_USER}
WORKDIR /workdir

ENTRYPOINT ["/ddmc/venv/bin/start"]