
import distutils.spawn
import sys

from ats.aic.misc import AICCommand

import six.moves.configparser as configparser


class Config(AICCommand):
    """
    creates or updates ansible.cfg
    """

    def take_action(self, parsed_args):
        inventory = distutils.spawn.find_executable('aic-inventory')

        self.log.info('redirect the following to ansible.cfg')
        cp = configparser.ConfigParser()
        cp.add_section('defaults')
        cp.set('defaults', 'inventory', inventory)
        cp.set('defaults', 'host_key_checking', True)
        cp.set('defaults', 'remote_user', 'ubuntu')
        cp.set('defaults', 'private_key_file', self.private_ssh_key)
        cp.set('defaults', 'nocows', True)
        cp.set('defaults', 'retry-files-enabled', False)
        cp.write(sys.stdout)
