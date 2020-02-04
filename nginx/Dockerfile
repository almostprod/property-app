FROM nginx:1.15

ARG CERT_DIR="/etc/letsencrypt/live/property.almostproductive.com/"

RUN mkdir -p ${CERT_DIR}

ADD fullchain.pem ${CERT_DIR}
ADD privkey.pem ${CERT_DIR}
ADD default.conf /etc/nginx/conf.d/default.conf
ADD .htpasswd /etc/nginx/.htpasswd
