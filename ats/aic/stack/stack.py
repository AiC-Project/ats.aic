
from pkg_resources import resource_filename

from ats.aic.lib.wait_net_service import wait_net_service
from ats.aic.misc import AICCommand, fetch_stackoutput
from ats.aic.exceptions import BuildFailure


def stack_name(conf, choice):
    if choice == 'network':
        return 'network'
    return '%s-%s' % (conf.cluster, choice)


server_stacks = ['controller', 'ats', 'sdl']
infra_stacks = ['network']


def add_argument_flavor(parser):
    parser.add_argument(
        '--flavor',
        default=None,
        help='instance flavor',
    )


def add_argument_stack(parser):
    parser.add_argument(
        'stack',
        choices=server_stacks + infra_stacks,
        help='stack name (without prefix)',
    )


def stack_param_arguments(parsed_args):
    ret = []
    if parsed_args.flavor:
        ret.extend(['--parameter', 'flavor=%s' % parsed_args.flavor])
    return ret


class Create(AICCommand):
    """
    create a stack
    """

    def get_parser(self, prog_name):
        ap = super(Create, self).get_parser(prog_name)
        add_argument_flavor(ap)
        add_argument_stack(ap)
        return ap

    def take_action(self, parsed_args):
        sn = stack_name(self.conf, parsed_args.stack)

        self.log.info('Creating stack "%s".', sn)

        template = resource_filename('ats.aic',
                                     'resources/heat/%s.yaml' %
                                     parsed_args.stack)

        cmd = [
            'openstack', 'stack', 'create', '-t', template, '--wait',
            '--parameter', 'floating_net=%s' % self.conf.floating_net,
            '--parameter', 'key_name=%s' % self.conf.ssh_key_name,
        ]
        cmd.extend(stack_param_arguments(parsed_args))
        cmd.append(sn)

        self.call(*cmd)

        if parsed_args.stack == 'network':
            android_router_ip = fetch_stackoutput(sn, 'android_router_ip',
                                                  logger=self.log)
            self.log.warning('** The deployed VMs will have access to the OpenStack APIs, '
                             'through the router %s, unless a firewall is in place.' %
                             android_router_ip)
        else:
            ipgetter = lambda: fetch_stackoutput(sn, 'ip_floating',
                                                 logger=self.log)
            ip, _ = wait_net_service(ipgetter, 22, logger=self.log)

            if ip is None:
                raise BuildFailure('Could not retrieve ip address. '
                                   'Try to upgrade the python-heatclient')

            self.call('ssh-keygen', '-R', ip)

        self.log.info('Stack "%s" created and available.', sn)


class Update(AICCommand):
    """
    update a stack
    """

    def get_parser(self, prog_name):
        ap = super(Update, self).get_parser(prog_name)
        add_argument_flavor(ap)
        add_argument_stack(ap)
        return ap

    def take_action(self, parsed_args):
        sn = stack_name(self.conf, parsed_args.stack)

        self.log.info('Updating stack "%s".', sn)

        template = resource_filename('ats.aic',
                                     'resources/heat/%s.yaml' %
                                     parsed_args.stack)

        cmd = [
            'openstack', 'stack', 'update', '-t', template,
            '--parameter', 'floating_net=%s' % self.conf.floating_net,
            '--parameter', 'key_name=%s' % self.conf.ssh_key_name,
        ]

        cmd.extend(stack_param_arguments(parsed_args))
        cmd.append(sn)

        self.call(*cmd)

        self.log.info('Server "%s" is being updated.', sn)
        self.log.info('Please check the status with "openstack stack show %s" '
                      'before proceeding.', sn)


class ConsoleLog(AICCommand):
    """
    display the console log
    """

    def get_parser(self, prog_name):
        ap = super(ConsoleLog, self).get_parser(prog_name)
        ap.add_argument(
            'stack',
            choices=server_stacks,
            help='stack to examine',
        )
        return ap

    def take_action(self, parsed_args):
        sn = stack_name(self.conf, parsed_args.stack)
        self.call('openstack', 'console', 'log', 'show', sn)


class SSH(AICCommand):
    """
    connect to a server
    """

    def get_parser(self, prog_name):
        ap = super(SSH, self).get_parser(prog_name)
        ap.add_argument(
            'stack',
            choices=server_stacks,
            help='stack of the server to connect to',
        )
        return ap

    def take_action(self, parsed_args):
        sn = stack_name(self.conf, parsed_args.stack)

        self.log.info('Connecting to server "%s".', sn)

        wait_net_service(lambda: fetch_stackoutput(sn, 'ip_floating', logger=self.log),
                         22, logger=self.log)

        self.call('openstack', 'server', 'ssh',
                  '-i', self.private_ssh_key,
                  '--login', 'ubuntu', sn)
