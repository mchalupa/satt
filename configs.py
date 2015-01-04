#!/usr/bin/env python
#
# Copyright (c) 2014 Marek Chalupa
# E-mail: statica@fi.muni.cz
#
# Permission to use, copy, modify, distribute, and sell this software and its
# documentation for any purpose is hereby granted without fee, provided that
# the above copyright notice appear in all copies and that both that copyright
# notice and this permission notice appear in supporting documentation, and
# that the name of the copyright holders not be used in advertising or
# publicity pertaining to distribution of the software without specific,
# written prior permission. The copyright holders make no representations
# about the suitability of this software for any purpose. It is provided "as
# is" without express or implied warranty.
#
# THE COPYRIGHT HOLDERS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO
# EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
#
# On arran we have only python2, so use python2

import sys
import os
import getopt
import time

allowed_keys = ['tool-dir', 'remote-dir', 'benchmarks', 'machines',
                'ssh-user', 'ssh-cmd', 'remote-cmd', 'sync', 'timeout',
                'no-db', 'sync-cmd', 'year']

def usage():
    sys.stderr.write(
"""
Static analysis tools tester, 2014
-------------------------------------

Usage: satt OPTS tool

OPTS can be:
    --machines=file.txt             File with machines
    --benchmarks=dir/set_file       Directory with sets of benchmarks or set file
    --no-sync                       Do not sync tool on remote machines
    --sync=[yes/no]                 Whether to sync tool on remote machines
    --debug                         Enable debugging messages
    --no-db                         Do not store result to database
    --year=[year]                   Specify year

These options can be specified in config file (except for 'debug' and 'no-db')

Each tool is supposed to have its own directory with config files and
scripts that will run the tool on remote computers. Basically, all that
is needed is:
tool_dir  \
    config
    remote_runner
    remote_sync (optional)

In config file, there are few keys that is searched for:
tool-dir      -- directory that contains the tool
remote-dir    -- where will we work on remote machines
remote-cmd    -- command to run the test on remote computer. This command
                 is run _localy_, so it will probably begin with: ssh user@{machine}
timeout       -- timeout for tests
sync-cmd      -- run this command before running tests to sync tool on remote
                 computers
year          -- specify year of sv-comp. The benchmarks will be searched for in
                 {benchmarks}/{year}

In configuration file can be comments (line begining with #) and in variables can
be used another variables in {var} that will be expaneded. Example:

tool-dir = tooler
remote-dir = ~/{tool-dir}

There are two special variables {benchmark} (synonym {file}) and {machine}
that will expand to current benchmark file and remote machine.

Command-line argument have higher priority. Tool defaults to 'symbiotic'

Allowed keys in config file:
""")

    i = 0
    for k in allowed_keys:
        sys.stderr.write(k)

        i += 1
        if i % 3 == 0:
            sys.stderr.write('\n')
        else:
            sys.stderr.write('\t')


# fill in default values
configs = {'sync':'yes', 'ssh-user':'', 'remote-dir':'',
           'remote-cmd':'echo "ERROR: No command specified"',
           'no-db':'no', 'debug':'no', 'tool':'symbiotic',
           'year':time.strftime('%Y')}

def parse_configs(path = 'symbiotic/config'):
    from common import err, dbg

    if os.path.exists(path):
        print('Using config file {0}'.format(path))
    else:
        return configs

    try:
        f = open(path, 'r')
    except IOError as e:
        err("Failed opening configuration file ({0}): {1}"
            .format(path, e.strerror))

    for line in f:
        line = line.strip()
        if not line or line[0] == '#':
            continue

        key, val = line.split('=', 1)
        key = key.strip()
        val = val.strip()

        if key in allowed_keys:
            configs[key] = val
        else:
            err('Unknown config key: {0}'.format(key))

    return configs

def parse_command_line():
    from common import err, dbg

    try:
        opts, args = getopt.getopt(sys.argv[1:], '',
                                  ['help', 'machines=', 'benchmarks=',
                                   'no-sync', 'no-db', 'sync=', 'debug',
                                   'year='])
    except getopt.GetoptError as e:
        err('{0}'.format(str(e)))

    for opt, arg in opts:
        if opt == '--help':
            usage()
            sys.exit(1)
        elif opt == '--machines':
            configs['machines'] = arg
        elif opt == '--benchmarks':
            configs['benchmarks'] = arg
        elif opt == '--no-sync':
            configs['sync'] = 'no'
        elif opt == '--sync':
            configs['sync'] = arg
        elif opt == '--no-db':
            configs['no-db'] = 'yes'
        elif opt == '--debug':
            configs['debug'] = 'yes'
        elif opt == '--year':
            configs['year'] = arg
        else:
            err('Unknown switch {0}'.format(opt))

    if len(args) > 1:
        usage()
        sys.exit(1)
    elif len(args) == 1:
        configs['tool'] = args[0]

    # print debug
    for l, r in configs.items():
        dbg('{0} = {1}'.format(l, r))

    return configs['tool']