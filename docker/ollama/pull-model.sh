#!/bin/sh
# Optional helper: pull the default local model after Ollama is up.
set -e
echo "Waiting for Ollama..."
until curl -sf http://ollama:11434/api/tags >/dev/null 2>&1; do
  sleep 2
done
echo "Pulling model ${OLLAMA_MODEL:-llama3.2}..."
ollama pull "${OLLAMA_MODEL:-llama3.2}" || true
echo "Done."
