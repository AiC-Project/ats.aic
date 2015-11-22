
from pathlib import Path

import cliff.app
import colorlog

from ats.aic.lib.config import fetch_conf


class AICApp(cliff.app.App):

    def log_formatter(self):
        return colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(cyan)s%(message)s",
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            }
        )

    def initialize_app(self, *args, **kw):
        self.workpath = Path('.').absolute()
        config_path = Path('etc/config-controller.yml')
        self.conf = fetch_conf(config_path,
                               logger=self.LOG)
        super(AICApp, self).initialize_app(*args, **kw)
