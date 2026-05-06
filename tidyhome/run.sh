#!/usr/bin/with-contenv bashio

export LOG_LEVEL="$(bashio::config 'log_level')"
export ADMINS="$(bashio::config 'admins')"

bashio::log.info "TidyHome startet (Log: ${LOG_LEVEL}, Admins: ${ADMINS:-keine})..."

exec python3 /app/main.py
