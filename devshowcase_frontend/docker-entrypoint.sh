#!/bin/sh
# Railway provides $PORT â€” substitute it in the nginx config
PORT=${PORT:-80}
sed -i "s/listen 80;/listen $PORT;/" /etc/nginx/conf.d/default.conf
exec nginx -g "daemon off;"
