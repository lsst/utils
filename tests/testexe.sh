#!/bin/sh

# Simple executable shell script.
# By default does nothing and exits with 0 status.
# with "-f" option, exits with a status of 1

while getopts "fh" opt; do
  case "$opt" in
  f)
    echo "Triggering bad exit status"
    exit 1
    ;;
  *)
    ;;
  esac
done

echo "Completing test script without error"
