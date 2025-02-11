#!/bin/bash

# Replace the next shell command with the entrypoint of your solution

# python3 './HTTP Protocol/http_terminal.py' "$@"

method=""
url=""
headers=""
data=""

while getopts ":m:u:h:d:" opt; do
  case $opt in
    m) method="$OPTARG" ;;
    u) url="$OPTARG" ;;
    h) headers="$OPTARG" ;;
    d) data="$OPTARG" ;;
    \?) echo "Opción inválida: -$OPTARG" >&2
        exit 1
        ;;
    :) echo "La opción -$OPTARG requiere un argumento." >&2
       exit 1
       ;;
  esac
done

if [ -z "$method" ] || [ -z "$url" ]; then
  echo "Uso: $0 -m <method> -u <url> -h <headers> -d <data>"
  exit 1
fi

export PYTHONPATH=$PWD
python3 HTTP Protocol/http_terminal.py -m "$method" -u "$url" -h "$headers" -d "$data"