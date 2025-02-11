#!/bin/bash

method=""
url=""
headers=""
data=""

<<<<<<< HEAD
=======
# python3 './HTTP Protocol/http_terminal.py' "$@"

method=""
url=""
headers=""
data=""

>>>>>>> 395033d427c1a23b8d62fae5ab65526f510e8eb5
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

<<<<<<< HEAD
python3 ./HTTP_Protocol/client.py -m "$method" -u "$url" -H "$headers" -d "$data"
=======
export PYTHONPATH=$PWD
python3 HTTP Protocol/http_terminal.py -m "$method" -u "$url" -h "$headers" -d "$data"
>>>>>>> 395033d427c1a23b8d62fae5ab65526f510e8eb5
