
import sys

from cliff.commandmanager import CommandManager

import ats.aic
from ats.aic.lib.app import AICApp


class App(AICApp):

    def __init__(self):
        super(App, self).__init__(
            description='aic-stack',
            version=ats.aic.version,
            command_manager=CommandManager('aic_stack'))


def main(argv=sys.argv[1:]):
    app = App()
    return app.run(argv)
