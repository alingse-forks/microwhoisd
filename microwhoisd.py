#!/usr/bin/env python3

import os, sys, argparse, pwd, grp, socket, socketserver, re, yaml, ipaddress

def parseArgs():
	parser = argparse.ArgumentParser(description='Micro implementation of an whois server.', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('--listen', dest='address', default='localhost', help='Address to listen on (default: localhost)')
	parser.add_argument('--port', dest='port', type=int, default=43, help='Port (default: 43)')
	parser.add_argument('--config', dest='config_path', default='config.yaml', help='Config file (default: config.yaml)')
	parser.add_argument('--uid', default='nobody', help='Run with this user after creating socket (default: nobody)')
	parser.add_argument('--gid', default='nobody', help='Run with this group after creating socket (default: nobody)')

	args = parser.parse_args()

	return (args.address, args.port, args.config_path, args.uid, args.gid)

def dropRoot(uid, gid):
    uid_name = uid
    gid_name = gid

    try:
            running_uid = pwd.getpwnam(uid_name).pw_uid
    except KeyError:
            print('The user \'%s\' does not exist. Create it or change the user with the option --uid' % uid)
            sys.exit(1)

    try:
            running_gid = grp.getgrnam(gid_name).gr_gid
    except KeyError:
            print('The group \'%s\' does not exist. Create it or change the group with the option --gid' % gid)
            sys.exit(1)

    os.setgroups([])
    os.setgid(running_gid)
    os.setuid(running_uid)

class Network:

    def __init__(self, config):

        self.name = config['name']
        self.subnet = ipaddress.ip_network(config['subnet'])

        if 'vlan' in config:
            self.vlan = config['vlan']
        else:
            self.vlan = None

        if 'gateway' in config:
            self.gateway = ipaddress.ip_address(config['gateway'])
        else:
            self.gateway = None

    def contains(self, ip):
        return ipaddress.ip_address(ip) in self.subnet

    def info(self):
        text = "Network name: %s\n" % self.name
        text += "Subnet: %s\n" % self.subnet
        text += "Netmask: %s\n" % self.subnet.netmask
        if self.gateway:
            text += "Gateway: %s\n" % self.gateway
        if self.vlan:
            text += "VLAN: %s\n" % self.vlan
        return text

class Whois:

    def __init__(self, config):

        self.files = []
        self.keyvalues = {}
        self.networks = []

        if 'files' in config:
            self.files = config['files']

        if 'keyvalues' in config:
            self.keyvalues = config['keyvalues']

        if 'networks' in config:
            for network in config['networks']:
                try:
                    self.networks.append(Network(network))
                except ValueError as e:
                    print(e)


    def getResponse(self, query):

        # Hardcoded values override other entries

        if query in self.keyvalues:
            return self.keyvalues[query]

        # <network>.vlan - Return the network info

        match = re.match("^([^.]+).vlan$", query)

        if match:
            vlan = match.group(1)
            for network in self.networks:
                if network.vlan == vlan:
                    return network.info()

        # IP address - Return the network info matching the IP

        try:
            for network in self.networks:
                if network.contains(query):
                    return network.info()
        except ValueError:
            pass

        # Fallback to returning a line from the file matching the query given

        for f in self.files:
            try:
                with open(f, encoding='utf-8') as fp:

                    for record in fp:
                        fields = record.split()

                        if len(fields) < 1:
                            continue

                        if fields[0] == query:
                            return record
            except Exception as e:
                print(e)

        return ""

class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
            try:
                query = self.rfile.readline().rstrip().decode('utf-8')
            except UnicodeDecodeError as e:
                return
            self.wfile.write(bytes(whois.getResponse(query), 'utf-8'))

class V6Server(socketserver.TCPServer):
    address_family = socket.AF_INET6

if __name__ == "__main__":

    (listen_address, port, config_path, uid, gid) = parseArgs()

    with open(config_path) as stream:
        try:
            whois = Whois(yaml.load(stream))
        except yaml.YAMLError as e:
            print(e)

    socketserver.TCPServer.allow_reuse_address = True

    try:
        try:
            server = V6Server((listen_address, port), TCPHandler)
        except OSError:
            # Use IPv4 socket
            server = socketserver.TCPServer((listen_address, port), TCPHandler)

    except socket.error as e:
        print('Could not open socket on port %d. Are you root? (%s)' % (port, e))
        sys.exit()

    if os.geteuid() == 0:
        dropRoot(uid, gid)

    server.serve_forever()
