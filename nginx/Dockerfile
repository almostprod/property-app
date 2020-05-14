FROM nginx:1.15

RUN mkdir -p /ssl/

ADD ./local.almostproductive.com/fullchain.pem /ssl/
ADD ./local.almostproductive.com/privkey.pem /ssl/


ADD default.conf /etc/nginx/conf.d/default.conf
