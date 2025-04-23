#!/bin/sh

CONSUMER_KEY="$1"

if [ -z "$CONSUMER_KEY" ]; then
    echo "Usage: $0 <consumer_key>"
    exit 1
fi

set -x

REQUEST_CODE=$(curl -H "Content-Type: application/x-www-form-urlencoded" \
     -X POST \
     -d "consumer_key=$CONSUMER_KEY"
     https://getpocket.com/v3/oauth/request | cut -d '=' -f 2)


xdg-open https://getpocket.com/auth/authorize?request_token=$(REQUEST_CODE)
read -p "Press enter after authorizing the app in your browser..."


echo "Generating access_token. please store in tfvars"
curl  -H "Content-Type: application/x-www-form-urlencoded" https://getpocket.com/v3/oauth/authorize -d "consumer_key=107361-8ef7b5f947c06ed8c917482&code=224ea17b-a379-49dc-9cdc-ab2325"

set +x