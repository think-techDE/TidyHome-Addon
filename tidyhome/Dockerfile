ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip py3-virtualenv

WORKDIR /app
COPY app/ /app/

RUN python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r /app/requirements.txt

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
