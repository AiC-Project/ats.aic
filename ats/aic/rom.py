
import datetime
import json
from pathlib import Path

from six.moves import shlex_quote

from ats.aic.exceptions import BuildFailure, ExecutionFailure
from ats.aic.lib.askbool import askbool
from ats.aic.misc import AICCommand


class UploadImages(AICCommand):
    """
    upload the system + data images to the cloud
    """

    def get_parser(self, prog_name):
        ap = super(UploadImages, self).get_parser(prog_name)
        ap.add_argument('directory',
                        help='folder containing .vid and .metadata files')

        ap.add_argument(
            'postfix',
            help='image name postfix (default build_id + build_timestamp)',
        )

        return ap

    def upload_image(self, path, image, params=None, properties=None):
        self.log.info('Uploading %s to %s.', path.name, image)

        if properties is None:
            properties = {}

        do_upload = True

        while do_upload:
            try:
                image_output = self.call(
                    'openstack', 'image', 'show', image, '-f', 'json',
                    capture_err=True,
                    capture_out=True
                )['output']
            except ExecutionFailure:
                break

            js = json.loads(image_output)
            print('Found an existing image %s.' % image)

            # cannot convert owner to user id, needs admin access
            # for the required keystone api

            for key in ['owner', 'created_at', 'updated_at']:
                print(' - %s: %s' % (key, js[key]))
            if askbool('Do you want to replace it?', False):
                self.log.info('Removing image...')
                try:
                    self.call('openstack', 'image', 'delete', image)
                except ExecutionFailure as exc:
                    self.log.error(exc)
            else:
                do_upload = False

        if do_upload:
            cmd = ['openstack', 'image', 'create']
            if params:
                cmd.extend(params)

            for prop, value in properties.items():
                cmd.extend([
                    '--property',
                    '{}={}'.format(shlex_quote(prop), shlex_quote(value)),
                ])

            cmd.extend(['--file', path, image])
            self.log.info('Uploading...')
            self.call(*cmd)

    def take_action(self, parsed_args):
        system_path = Path(parsed_args.directory,
                           'android_system_disk.vdi')
        if not system_path.exists():
            raise BuildFailure('Image %s was not found. '
                               'Please run "aic rom build" and retry.' %
                               system_path)

        data_path = Path(parsed_args.directory,
                         'android_data_disk.vdi')
        if not data_path.exists():
            raise BuildFailure('Image %s was not found. '
                               'Please run "aic rom build" and retry.' %
                               data_path)

        metadata_path = Path(parsed_args.directory,
                             'android_system_disk.metadata')
        if not metadata_path.exists():
            raise BuildFailure('Build metadata %s was not found. '
                               'Please run "aic rom build" or forge the metadata by hand.' %
                               metadata_path)

        with Path(metadata_path).open() as fin:
            metadata = json.load(fin)

        if metadata_path.stat().st_mtime < system_path.stat().st_mtime:
            raise BuildFailure('Metadata is older than the current build. '
                               'Please run "aic rom build" or update the '
                               'metadata by hand in %s.' % metadata_path)

        self.log.info('Reading metadata from %s', metadata_path)
        for key, value in metadata.items():
            self.log.info('%s = %s', key, value)

        if parsed_args.postfix:
            postfix = parsed_args.postfix
        else:
            build_dt = datetime.datetime.fromtimestamp(int(metadata['build_timestamp']))
            postfix = '-'.join([metadata['build_id'], build_dt.strftime('%Y%m%d-%H%M%S')])

        self.upload_image(system_path,
                          image='system-%s' % postfix,
                          params=['--disk-format', 'vdi', '--min-disk', 2,
                                  '--min-ram', 512],
                          properties=metadata)

        self.upload_image(data_path,
                          image='data-%s' % postfix,
                          params=['--disk-format', 'vdi', '--min-disk', 3],
                          properties=metadata)

        self.log.info('Upload complete.')
