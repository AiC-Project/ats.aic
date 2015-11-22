
import json
import logging
from pathlib import Path
import sys

from ats.aic.lib.config import fetch_conf
from ats.aic.misc import fetch_stackoutput


def main(argv=sys.argv[1:]):
    conf = fetch_conf(Path('etc/config-controller.yml'),
                      logger=logging)

    cluster = conf.cluster

    if not len(argv) or argv[0] != '--list':
        sys.stderr.write('Please call the inventory with --list. '
                         'Other options are not supported.\n')
        sys.exit(1)

    hostvars = {}
    for name in ['controller', 'ats', 'sdl']:

        ip_floating = fetch_stackoutput('%s-%s' % (cluster, name), 'ip_floating',
                                        logger=logging)
        if ip_floating:
            hostvars[name] = {
                'ansible_host': ip_floating,
                'ip_floating': ip_floating,
                'ansible_python_interpreter': '/usr/bin/python2.7',
            }
        else:
            continue

        ip_service = fetch_stackoutput('%s-%s' % (cluster, name), 'ip_service',
                                       logger=logging)
        if ip_service:
            hostvars[name]['ip_service'] = ip_service

    inventory = {
        '_meta': {
            'hostvars': hostvars
        },
        'aic': {
            'hosts': [name for name in hostvars]
        }
    }

    print(json.dumps(inventory, indent=4))
