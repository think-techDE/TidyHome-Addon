#!/usr/bin/with-contenv bashio

export LOG_LEVEL="$(bashio::config 'log_level')"
export NOTIFY_SERVICE="$(bashio::config 'notify_service')"
export NOTIFY_TIME="$(bashio::config 'notify_time')"

bashio::log.info "TidyHome startet (Log: ${LOG_LEVEL}, Notify: ${NOTIFY_SERVICE:-aus} um ${NOTIFY_TIME:-08:00})..."

exec python3 /app/main.py
