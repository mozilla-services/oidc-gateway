#!/usr/bin/env python2

import subprocess
import yaml
import jinja2
import collections


def nginx_quote(s):
    s = s.replace('"', '\\"')
    return '"{}"'.format(s)


jinja2.filters.FILTERS["nginxquote"] = nginx_quote
jinja2.undefined = jinja2.StrictUndefined

def merge(dict1, dict2):
    for k, v in dict2.iteritems():
        if (
            k in dict1
            and isinstance(dict1[k], dict)
            and isinstance(dict2[k], collections.Mapping)
        ):
            merge(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]


def main():
    with open("config.yaml") as config_stream:
        config = yaml.safe_load(config_stream)
    with open("secrets.yaml") as secrets_stream:
        secrets = yaml.safe_load(secrets_stream)
    merge(config, secrets)
    with open("default.conf.jinja2", "r") as f:
        template = jinja2.Template(f.read())
    with open("/etc/nginx/conf.d/default.conf", "w") as f:
        print(template.render(config))
        f.write(template.render(config))
    subprocess.call(["openresty", "-g", "daemon off;"])


if __name__ == "__main__":
    main()
