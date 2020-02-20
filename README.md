# Microwhoisd

Small daemon to serve as an [WHOIS](https://en.wikipedia.org/wiki/WHOIS) server.

Useful to be able to internally use a standard whois client to get useful information on DNS names and IP addresses.

## Server Configuration

It uses an [YAML](https://en.wikipedia.org/wiki/YAML) configuration file
(see ``config-dist.yaml`` as an example),
where the answers can be configured from
multiple sources, returing the first that matches according to the order below.

### Keyvalues


Key/Value pairs can be hardcoded into the configuration, overriding other methods.


If the key matches the whois query, it returns the associated value.


```yaml
keyvalues:
  machine1: Description 1
```

Usage example:
```sh
$ whois machine1
Description 1
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

Usage example:
```sh
$ whois 192.168.1.100
Network name: Network 1
Subnet: 192.168.1.0/24
Netmask: 255.255.255.0
Gateway: 192.168.1.254
VLAN: network1
```

It will also return the network information for queries in the form ``<vlan name>.vlan``, like ``network1.vlan``.

Usage example:
```sh
$ whois network1.vlan
Network name: Network 1
Subnet: 192.168.1.0/24
Netmask: 255.255.255.0
Gateway: 192.168.1.254
VLAN: network1
```

### Files

If the previous methods fail to match,
the files given in the configuration will be scanned for matches.
If the first word matches the given query, the whole line is returned.

```yaml
files:                                                                                                                         
  - file1
  - file2
```

For example, assuming one of the files is a DNS zone file, you would get:

```sh
$ whois machine2
machine2		IN		A	192.168.1.2			; Machine2
```

## Launching the server

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

Without relying on whois client configuration,
the server can be tested by running the whois client like the following:

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

