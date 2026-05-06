ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app
COPY app/ /app/

RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
