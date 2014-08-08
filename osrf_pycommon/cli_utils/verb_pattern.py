# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pkg_resources
import inspect


def call_prepare_arguments(func, parser, sysargs=None):
    func_args = [parser]
    # If the provided function takes two arguments and args were given
    # also give the args to the function
    arguments = inspect.getargspec(func)[0]
    limit = 2
    if arguments[0] == 'self':
        limit = 3
    if len(arguments) == limit:
        func_args.append(sysargs or [])
    return func(*func_args) or parser


def create_subparsers(parser, cmd_name, verbs, group, sysargs, title=None):
    metavar = '[' + ' | '.join(verbs) + ']'
    subparser = parser.add_subparsers(
        title=title or '{0} command'.format(cmd_name),
        metavar=metavar,
        description='Call `{0} {1} -h` for help on a each verb.'.format(
            cmd_name, metavar),
        dest='verb'
    )

    argument_preprocessors = {}
    verb_subparsers = {}

    for verb in verbs:
        desc = load_verb_description(verb, group)
        cmd_parser = subparser.add_parser(
            desc['verb'], description=desc['description'])
        cmd_parser = call_prepare_arguments(
            desc['prepare_arguments'],
            cmd_parser,
            sysargs,
        )

        cmd_parser.set_defaults(main=desc['main'])

        if 'argument_preprocessor' in desc:
            argument_preprocessors[verb] = desc['argument_preprocessor']
        else:
            argument_preprocessors[verb] = default_argument_preprocessor
        verb_subparsers[verb] = cmd_parser

    return argument_preprocessors, verb_subparsers


def default_argument_preprocessor(args):
    extras = {}
    return args, extras


def list_verbs(group):
    verbs = []
    for entry_point in pkg_resources.iter_entry_points(group=group):
        verbs.append(entry_point.name)
    return verbs


def load_verb_description(verb_name, group):
    for entry_point in pkg_resources.iter_entry_points(group=group):
        if entry_point.name == verb_name:
            return entry_point.load()


def split_arguments_by_verb(arguments):
    verb = None
    pre_verb_args = []
    post_verb_args = []
    for index, arg in enumerate(arguments):
        # If the arg does not start with a `-` then it is a positional argument
        # The first positional argument must be the verb
        if not arg.startswith('-'):
            verb = arg
            post_verb_args = arguments[index + 1:]
            break
        # Otherwise it is a pre-verb option
        pre_verb_args.append(arg)
    return verb, pre_verb_args, post_verb_args
