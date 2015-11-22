
from pathlib import Path


from ats.aic.lib.env import environment
from ats.aic.lib.pushd import pushd
from ats.aic.misc import AICCommand


def frontend_path(local_src):
    return Path(local_src, 'frontend')


class Source(AICCommand):
    """
    clone the web frontend repository
    """

    def take_action(self, parsed_args):
        self.log.info('Cloning frontend.')

        self.call('git', 'clone',
                  '-b', self.conf.git.ats.ats_frontend.version,
                  self.conf.git.ats.ats_frontend.repo,
                  frontend_path(self.local_src),
                  '--recursive')

        self.log.info('Clone complete.')


class Build(AICCommand):
    """
    build the web frontend
    """

    def take_action(self, parsed_args):
        self.log.info('Building frontend.')

        with pushd(frontend_path(self.local_src),
                   if_missing='Please run "aic frontend source" and retry.'):
            frontend_tgz = Path(self.local_images, 'frontend.tgz')
            with environment({'NODE_ENV': 'production'}):
                self.call('make', 'clean', 'all')
                self.call('tar', 'cfz', frontend_tgz, 'build')

            self.log.info('Build complete in %s', frontend_tgz)
