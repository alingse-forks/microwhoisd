# Microwhoisd

Small daemon to serve as an WHOIS server.

## Configuration

It uses as YAML configuration file, where the answerers can be configured from
multiple sources, returing the first that matches according to the order below.

### Keyvalues

Key/Value pairs can be hardcoded into the configuration, overriding other methods.

If the key matches the whois query, it returns the associated value.

### Networks

TODO

### Files

TODO
