# OIDC Gateway

A Docker container and Kubernetes Helm chart that gates access to an upstream service
based on OpenID Connect authentication. It uses
[OpenResty](https://github.com/openresty/openresty) with
[lua-resty-openidc](https://github.com/zmartzone/lua-resty-openidc). Additionally, it
uses [Jinja2](http://jinja.pocoo.org/docs/2.10/) to template an NGINX config.

It proxies traffic on port 80. If you want to do TLS, you should terminate it before
sending the traffic to this gateway.

## Configuration

OIDC Gateway is configured through YAML files. Because parts of the configuration are
sensitive, it takes its configuration from both a ConfigMap and a Secret. The
sensitive parts belong in the Secret, and the non-sensitive ones belong in the
ConfigMap. The ConfigMap should contain a YAML file named `config.yaml` and the
Secret should contain a YAML file named `secrets.yaml`. These two files are merged,
with values from `secrets.yaml` taking precedence if they're present in both files.

The configuration looks as follows:

```yaml
# The upstream service to which to forward authenticated requests.
# E.g. "mozilla.com", "myservice". 
upstream: 'string'
oidc:
  # The OIDC client ID. E.g. '33PByFLjwvChUk7oaPcD5Z0egBtccacU'
  client_id: 'string'
  # The OIDC client secret.
  # E.g. 'vBOctKc8scalRP__62zh3oNbF2HJWh2lSeyo0EvNcHLpBbokNicnn86InRKlb2P4'
  client_secret: 'string'
  # The OIDC discovery URL.
  # E.g. 'https://auth.mozilla.auth0.com/.well-known/openid-configuration'
  discovery: 'string'
# Secret used to encrypt session data. E.g. '623q4hR325t36VsCD3g567922IC0073T'
session_secret: 'string'
```

You are free to decide what you want to keep secret and what you want to be public.

## Example

Suppose you have a Kubernetes service called `secretservice` that you want to gate
through OpenID Connect. Your OIDC provider gives you the following values:

- Discovery URL is `https://oidc.com/.well-known/openid-configuration`
- Client ID is `33PByFLjwvChUk7oaPcD5Z0egBtccacU`
- Client secret is `vBOctKc8scalRP__62zh3oNbF2HJWh2lSeyo0EvNcHLpBbokNicnn86InRKlb2P4`

You generate a random session secret, `6660b15ad13f9c5bd0b74767d00d05a3`.

You create the following ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: oidc-gateway
data:
  config.yaml: |
    upstream: secretservice
    oidc:
      client_id: '33PByFLjwvChUk7oaPcD5Z0egBtccacU'
      discovery: 'https://oidc.com/.well-known/openid-configuration'
```

And the following Secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth0-proxy
type: Opaque
data:
  secrets.yaml: b2lkYzoKICBjbGllbnRfc2VjcmV0OiB2Qk9jdEtjOHNjYWxSUF9fNjJ6aDNvTmJGMkhKV2gybFNleW8wRXZOY0hMcEJib2tOaWNubjg2SW5SS2xiMlA0CnNlc3Npb25fc2VjcmV0OiA2NjYwYjE1YWQxM2Y5YzViZDBiNzQ3NjdkMDBkMDVhMwo=
```

The base64-encoded string under `secrets.yaml` decodes to:

```yaml
oidc:
  client_secret: vBOctKc8scalRP__62zh3oNbF2HJWh2lSeyo0EvNcHLpBbokNicnn86InRKlb2P4
session_secret: 6660b15ad13f9c5bd0b74767d00d05a3
```

Apply these manifests onto your cluster.

You can then use a command like the following to deploy an instance of the
gateway. Make sure to pick an appropriate values for all the arguments.

```bash
helm template . \
  --set config.configMap=oidc-gateway \
  --set config.secret=oidc-gateway \
  --set app=secretservice \
  -n boring-wozniak | kubectl apply -f -
```  

This will create a Deployment and a Service. It is up to you to direct HTTP traffic
to the Service. You can use an Ingress or pass `--set service.type=LoadBalancer` to
the `helm` invocation, for example.

## Future plans

- Support redis and/or memcached for session storage so we can scale beyond one pod.
