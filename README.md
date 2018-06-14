# Microwhoisd

Small daemon to serve as an [WHOIS](https://en.wikipedia.org/wiki/WHOIS) server.

Useful to be able to internally use a standard whois client to get useful information on DNS names and IP addresses.

## Server Configuration

It uses as [YAML](https://en.wikipedia.org/wiki/YAML) configuration file (see the ``config-dist.yaml`` as example), where the answerers can be configured from
multiple sources, returing the first that matches according to the order below.

### Keyvalues


Key/Value pairs can be hardcoded into the configuration, overriding other methods.


If the key matches the whois query, it returns the associated value.


```yaml
keyvalues:
  key1: value1
```


### Networks

Subnets can be defined to return useful information when giving an IP address to whois.

```yaml
networks:
  - name: Network 1
    subnet: 192.168.1.0/24
    gateway: 192.168.1.254
    vlan: network1

```

### Files

If the previous methods fail to match, it will scan the files and if the first word matches
the given query it returns the whole line.

```yaml
files:                                                                                                                         
  - file1
  - file2
```

## Server launch

```
./microwhoisd --help
usage: microwhoisd.py [-h] [--listen ADDRESS] [--port PORT]
                      [--config CONFIG_PATH] [--uid UID] [--gid GID]

Micro implementation of an whois server.

optional arguments:
  -h, --help            show this help message and exit
  --listen ADDRESS      Address to listen on (default: localhost)
  --port PORT           Port (default: 43)
  --config CONFIG_PATH  Config file (default: config.yaml)
  --uid UID             Run with this user after creating socket (default: nobody)
  --gid GID             Run with this group after creating socket (default: nobody)
```

The daemon can be tested locally and without root permissions:


```
./microwhoisd --config config-dist.yaml --port 4343
```

And to run in production on the default whois port:

```
./microwhoisd --config /etc/microwhoisd.yaml --listen ::
```

## Client configuration

Withou any previous configuration, it can be tested by running the whois client like the following:

```
whois -h server -p port query
```

The port can be omitted if the server is running on the default port 43.


To be able to call the whois command without any extra arguments, configure the /etc/whois.conf like the following:

```
\.domain\.tld$                 server.domain
\.vlan$                        server.domain
^[^\.]+$                       server.domain   # Matches any name without domain

^10.16.                        server.domain
^192.168.                      server.domain
```

This way, when querying a single name or IP from those subnets, the whois client will query our server instead of the defaults.

