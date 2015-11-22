
from ats.aic.misc import AICLister, fetch_stackoutput


class List(AICLister):
    """
    display servers and IPs
    """

    def public_ip_list(self):
        ret = []
        for role in ['ats', 'sdl', 'controller']:
            stack_name = '%s-%s' % (self.conf.cluster, role)
            public_ip = fetch_stackoutput(stack_name, 'ip_floating', logger=self.log)
            if public_ip:
                ret.append([role, public_ip])
        return ret

    def take_action(self, parsed_args):
        self.log.info('Looking for servers in cluster "%s"', self.conf.cluster)
        floating_ips = self.public_ip_list()
        fields = ['alias', 'ip']
        if not floating_ips:
            self.log.info('No server found.')
        return fields, floating_ips
