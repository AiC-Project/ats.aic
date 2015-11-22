
from pathlib import Path

from ats.aic.lib.pushd import pushd
from ats.aic.misc import AICCommand


def player_path(local_src):
    return Path(local_src, 'player')


def player_camera_path(local_src):
    return Path(local_src, 'player.camera')


def player_compose_path(local_src):
    return Path(local_src, 'player.compose')


def dslcc_path(local_src):
    return Path(local_src, 'ats.dslcc')


def testcc_path(local_src):
    return Path(local_src, 'ats.testcc')


class Source(AICCommand):
    """
    clone the Player repository
    """

    def take_action(self, parsed_args):
        self.log.info('Cloning Player.')
        self.call('git', 'clone',
                  '-b', self.conf.git.sdl.player.version,
                  self.conf.git.sdl.player.repo,
                  player_path(self.local_src))

        self.log.info('Cloning player.camera')
        self.call('git', 'clone',
                  '-b', self.conf.git.sdl.player_camera.version,
                  self.conf.git.sdl.player_camera.repo,
                  player_camera_path(self.local_src))

        self.log.info('Cloning Player compose.')
        self.call('git', 'clone',
                  '-b', self.conf.git.sdl.player_compose.version,
                  self.conf.git.sdl.player_compose.repo,
                  player_compose_path(self.local_src))

        self.log.info('Cloning DSL -> Java compiler.')
        self.call('git', 'clone',
                  '-b', self.conf.git.sdl.dslcc.version,
                  self.conf.git.sdl.dslcc.repo,
                  dslcc_path(self.local_src))

        self.log.info('Cloning Java -> APK compiler.')
        self.call('git', 'clone',
                  '-b', self.conf.git.sdl.testcc.version,
                  self.conf.git.sdl.testcc.repo,
                  testcc_path(self.local_src))

        self.log.info('Clone complete.')


class BuildFbADB(AICCommand):
    """
    rebuilds the fb-adb CLI tool
    """

    def take_action(self, parsed_args):
        fbadb_path = Path(player_compose_path(self.local_src), 'fb-adb')

        target_adb = Path(player_compose_path(self.local_src), 'adb', 'fb-adb')

        with pushd(fbadb_path,
                   if_missing='Please run "aic player source" and retry.'):
            self.call('docker', 'build', '-t', 'fb-adb', '.')
            proc = self.call('docker', 'run', '--rm', '-d',
                             'fb-adb', 'tail', '-f', '/dev/null',
                             capture_out=True)
            container_id = proc['output'].strip()
            self.call('docker', 'cp',
                      '{}:/home/developer/fb-adb/build/fb-adb'.format(container_id),
                      target_adb)


class Build(AICCommand):
    """
    build the Player Docker image
    """

    def take_action(self, parsed_args):

        # Player

        self.log.info('Building Player binaries + images.')
        with pushd(player_path(self.local_src),
                   if_missing='Please run "aic player source" and retry.'):
            self.call('make', 'docker-all')

        # player.camera

        self.log.info('Building player.camera binary + image.')
        with pushd(player_camera_path(self.local_src),
                   if_missing='Please run "aic player source" and retry.'):
            self.call('make', 'docker-all')

        # Docker-compose images

        self.log.info('Building Player misc. Images.')
        with pushd(player_compose_path(self.local_src),
                   if_missing='Please run "aic player source" and retry.'):
            self.call('make', 'clean', 'docker-images')

        with pushd(dslcc_path(self.local_src),
                   if_missing='Please run "aic player source" and retry.'):
            self.call('make', 'clean', 'docker-images')

        with pushd(testcc_path(self.local_src),
                   if_missing='Please run "aic player source" and retry.'):
            self.call('make', 'clean', 'docker-images')

        self.log.info('Saving docker images...')

        docker_images_tar = Path(self.local_images, 'docker-images.tar')

        self.call('docker', 'save', '-o',
                  docker_images_tar.as_posix(),
                  'aic.adb', 'aic.audio', 'aic.avmdata', 'aic.camera', 'aic.dslcc',
                  'aic.ffserver', 'aic.prjdata', 'aic.sdl', 'aic.sensors',
                  'aic.testcc', 'aic.xorg')

        self.log.info('Build complete in %s', docker_images_tar)
