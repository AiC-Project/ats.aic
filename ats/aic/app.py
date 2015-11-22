
import sys

from cliff.commandmanager import CommandManager

import ats.aic
from ats.aic.lib.app import AICApp


class App(AICApp):

    def __init__(self):
        super(App, self).__init__(
            description='aic',
            version=ats.aic.version,
            command_manager=CommandManager('aic'))


def main(argv=sys.argv[1:]):
    app = App()
    return app.run(argv)
