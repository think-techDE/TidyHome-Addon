#!/usr/bin/with-contenv bashio

LOG_LEVEL=$(bashio::config 'log_level')
export LOG_LEVEL

bashio::log.info "TidyHome startet (Log-Level: ${LOG_LEVEL})..."

exec /venv/bin/python3 /app/main.py
