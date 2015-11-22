
from ats.aic.exceptions import ExecutionFailure
from ats.aic.misc import AICCommand, fetch_stackoutput



def fetch_ats_floating_ip(cluster, log):
    return fetch_stackoutput('%s-ats' % cluster, 'ip_floating',
                             logger=log)


class Frontend(AICCommand):
    """
    connect to the ATS frontend
    """

    def take_action(self, parsed_args):
        self.log.info('Opening browser.')

        url = 'https://%s:8443' % fetch_ats_floating_ip(self.conf.cluster, self.log)
        try:
            self.call('sensible-browser', url, log_level='INFO')
        except ExecutionFailure:
            self.log.info('Browser not available.')


class AMQP(AICCommand):
    """
    connect to the AMQP admin UI
    """

    def take_action(self, parsed_args):
        self.log.info('Opening browser.')

        url = 'http://%s:15672' % fetch_ats_floating_ip(self.conf.cluster, self.log)
        try:
            self.call('sensible-browser', url, log_level='INFO')
        except ExecutionFailure:
            self.log.info('Browser not available.')
