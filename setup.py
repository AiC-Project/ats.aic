#!/usr/bin/env python2
# vim: set ai ts=8 sts=4 sw=4 et:

import ats.aic

from setuptools import setup, find_packages

PROJECT = 'ats.aic'

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=ats.aic.version,

    description='AiC',
    long_description=long_description,

    author='Jenkins',
    author_email='jenkins@rnd.alterway.fr',

    install_requires=[
        'ansible',
        'attrdict',
        'cliff',
        'colorlog',
        'pathlib',
        'pollute',
        'python-heatclient',
        'python-openstackclient',
        'six',
    ],

    extras_require={
        'docs': (
            'sphinx',
            'sphinx_rtd_theme',
            'sphinxcontrib-programoutput',
        )},
    namespace_packages=['ats'],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'aic = ats.aic.app:main',
            'aic-inventory = ats.aic.inventory.app:main',
            'aic-stack = ats.aic.stack.app:main',
        ],
        # for Cliff
        'aic_stack': [
            'create = ats.aic.stack.stack:Create',
            'update = ats.aic.stack.stack:Update',
            'console-log = ats.aic.stack.stack:ConsoleLog',
            'ssh = ats.aic.stack.stack:SSH',
            'upload ubuntu = ats.aic.stack.images:Ubuntu',
            'upload sdcard = ats.aic.stack.images:Sdcard',
            'list = ats.aic.stack.servers:List',
        ],
        'aic': [
            'ansible-config = ats.aic.ansible:Config',
            'rom upload = ats.aic.rom:UploadImages',
            'frontend source = ats.aic.frontend:Source',
            'frontend build = ats.aic.frontend:Build',
            'player source = ats.aic.player:Source',
            'player fb-adb build = ats.aic.player:BuildFbADB',
            'player build = ats.aic.player:Build',
            'player upload = ats.aic.player_upload:Upload',
            'install = ats.aic.install:Install',
            'browser frontend = ats.aic.browser:Frontend',
            'browser amqp = ats.aic.browser:AMQP',
        ]
    },

    zip_safe=False,
)
