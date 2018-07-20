FROM openresty/openresty:1.13.6.2-0-centos-rpm

RUN yum install -y python-jinja2 python-yaml
RUN luarocks install lua-resty-openidc
COPY ./access_by_openidc.lua /opt/openresty/lualib/resty/access_by_openidc.lua

RUN mkdir /app
WORKDIR /app
COPY docker_entrypoint.py .
COPY default.conf.jinja2 .

CMD ["./docker_entrypoint.py"]
