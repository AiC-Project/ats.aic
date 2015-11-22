
import distutils.spawn
import json
from pathlib import Path
from pkg_resources import resource_filename

from ats.aic.lib.config import fetch_conf
from ats.aic.lib.env import environment
from ats.aic.misc import AICCommand


class Upload(AICCommand):
    """
    upload a set of player images
    """

    def get_parser(self, prog_name):
        ap = super(Upload, self).get_parser(prog_name)
        ap.add_argument(
            '--host-key-checking',
            dest='keycheck',
            action='store_true'
        )
        ap.add_argument(
            '--no-host-key-checking',
            dest='keycheck',
            action='store_false'
        )
        ap.set_defaults(keycheck=True)
        return ap

    def take_action(self, parsed_args):
        self.log.info('Uploading player images.')

        playbooks = Path(resource_filename('ats.aic', 'resources/ansible'))

        inventory = distutils.spawn.find_executable('aic-inventory')

        extravars = fetch_conf(Path(self.local_etc, 'config-controller.yml'),
                               logger=self.log)

        # we can't pass --extra-vars multiple times, will use it as a dict
        extravars['local_src'] = self.local_src.absolute().as_posix()
        extravars['local_etc'] = self.local_etc.absolute().as_posix()
        extravars['local_images'] = self.local_images.absolute().as_posix()

        cmd = [
            'ansible-playbook',
            Path(playbooks, 'sdl-docker-upload.yml'),
            '--inventory-file', inventory,
            '--user', 'ubuntu',
            '--private-key', self.private_ssh_key,
            '--extra-vars', json.dumps(extravars)
        ]

        if not parsed_args.keycheck:
            cmd.extend([
                '--ssh-extra-args',
                '-o "StrictHostKeyChecking=no"'
            ])

        ansible_env = {
            'ANSIBLE_CALLBACK_WHITELIST': 'profile_tasks',
            'ANSIBLE_SSH_PIPELINING': '1',
            'ANSIBLE_RETRY_FILES_ENABLED': '0',
        }

        with environment(ansible_env):
            self.call(*cmd)

        self.log.info('Upload complete.')
