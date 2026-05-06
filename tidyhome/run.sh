#!/usr/bin/with-contenv bashio

export LOG_LEVEL="$(bashio::config 'log_level')"

bashio::log.info "TidyHome startet (Log-Level: ${LOG_LEVEL})..."

exec python3 /app/main.py
