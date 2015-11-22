
import copy
import collections
import logging

import os
from pkg_resources import resource_stream
import stat
import sys

import attrdict

import yaml

from ats.aic.exceptions import ConfigurationError


def deep_update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = deep_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def check_config_security(path):
    st = path.stat()

    if st.st_mode & stat.S_IWGRP:
        raise ConfigurationError('%s is group writable' % path)

    if st.st_mode & stat.S_IWOTH:
        raise ConfigurationError('%s is world writable' % path)

    current_uid = os.getuid()

    if st.st_uid != current_uid:
        raise ConfigurationError('%s has owner %s, expected %s' %
                                 (path, st.st_uid, current_uid))


def fetch_conf(config_path, logger):
    with resource_stream('ats.aic', 'resources/ansible/controller-vars.yml') as fin:
        defaults = yaml.load(fin)

    if not config_path.exists():
        logging.error("Cannot find '%s': please run the command "
                      'from the workspace directory.' % config_path)
        sys.exit(1)

    check_config_security(config_path)

    with config_path.open() as fin:
        userconfig = yaml.load(fin)

    config = copy.deepcopy(defaults)
    config = deep_update(config, userconfig)

    return attrdict.AttrDict(config)
