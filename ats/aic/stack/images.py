
from pkg_resources import resource_filename

from ats.aic.exceptions import ExecutionFailure
from ats.aic.lib.pushd import pushd
from ats.aic.misc import AICCommand


class Sdcard(AICCommand):
    def take_action(self, parsed_args):
        fnames = [
            'sdcard-1g',
            'sdcard-2g',
            'sdcard-4g',
        ]

        for fname in fnames:
            self.log.info('Checking if %s already exists.' % fname)

            image_file = resource_filename('ats.aic',
                                           'resources/images/%s' % fname)
            try:
                self.call('openstack', 'image', 'show', fname)
                self.log.info('Image already exists, nothing to do.')
            except ExecutionFailure:
                self.upload_image(image_file, fname)
                self.log.info('Done.')

    def upload_image(self, image_file, fname):
        self.log.info('Uploading to OpenStack...')

        self.call('openstack',
                  'image', 'create',
                  '--container-format', 'bare',
                  '--disk-format', 'qcow2',
                  '--file', image_file,
                  fname)


class Ubuntu(AICCommand):
    """
    upload the Ubuntu cloud image on OpenStack
    """

    def take_action(self, parsed_args):
        version = '16.04'
        fname = 'ubuntu-%s-server-cloudimg-amd64-disk1.img' % version

        self.log.info('Checking if %s already exists.' % fname)

        try:
            self.call('openstack', 'image', 'show', fname)
            self.log.info('Image already exists, nothing to do.')
        except ExecutionFailure:
            self.download_image(self.local_images, fname, version)
            self.upload_image(self.local_images, fname)
            self.log.info('Done.')

    def download_image(self, imgp, fname, version):
        self.log.info('Downloading the %s Ubuntu image.' % version)

        with pushd(imgp):
            url = 'https://cloud-images.ubuntu.com/releases/%s/release/%s' % (
                version, fname
            )
            self.call('curl', '--remote-name', url)

    def upload_image(self, imgp, fname):
        self.log.info('Uploading to OpenStack...')

        with pushd(imgp):
            self.call('openstack',
                      'image', 'create',
                      '--container-format', 'bare',
                      '--disk-format', 'qcow2',
                      '--min-disk', 0,
                      '--min-ram', 0,
                      '--file', fname,
                      fname)
