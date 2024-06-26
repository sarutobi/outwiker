# -*- coding: utf-8 -*-

import argparse

import outwiker


class CommandLineException(Exception):
    pass


class _SilentParser(argparse.ArgumentParser):
    """Создаем производный класс от ArgumentParser, чтобы отключить
автоматический показ справки в случае ошибок в параметрах."""

    def error(self, message):
        raise CommandLineException


class CommandLine(object):
    """Класс для хранения разобранных параметров командной строки"""

    def __init__(self):
        self._description = 'OutWiker {ver}. Crossplatform program to keep your notes in a tree.'.format(
            ver=outwiker.getVersionStr())

        self._parser = self._createParser()
        self._namespace = None

    def parseParams(self, args):
        """
        args - параметры командной строки (исключая outwiker.py или outwiker.exe), т.е. это argv[1:]
        """
        try:
            self._namespace = self._parser.parse_args(args)
        except SystemExit:
            raise CommandLineException

    def _createParser(self):
        parser = _SilentParser(prog='outwiker',
                               description=self._description,
                               epilog='(c) Eugeniy Ilin (aka Jenyay), 2010-2019. Released under the GNU GPL 3.',
                               add_help=False)

        parser.add_argument('wikipath',
                            nargs='?',
                            metavar='path',
                            help='Path to notes tree')

        parser.add_argument('--page', '-p',
                            help='Subpath or UID of a page')

        parser.add_argument('--help', '-h',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Help')

        parser.add_argument('--version', '-v',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Version info')

        parser.add_argument('--readonly', '-r',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Open wiki as read only')

        parser.add_argument('--normal',
                            action='store_const',
                            const=True,
                            default=False,
                            help="Don't minimize window when starting",
                            dest='disableMinimizing')

        parser.add_argument('--debug',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Enable debug mode',
                            dest='debug')

        parser.add_argument('--disable-plugins',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Disable all plug-ins',
                            dest='disablePlugins')

        return parser

    @property
    def wikipath(self):
        result = None

        if self._namespace.wikipath is not None:
            result = self._namespace.wikipath
            if len(result.split()) == 0:
                result = None

        return result

    @property
    def page_id(self):
        result = None

        if self._namespace.page is not None:
            result = self._namespace.page
            if len(result.split()) == 0:
                result = None

        return result

    @property
    def help(self):
        return self._namespace.help

    @property
    def readonly(self):
        return self._namespace.readonly

    @property
    def version(self):
        return self._namespace.version

    @property
    def disableMinimizing(self):
        return self._namespace.disableMinimizing

    @property
    def debug(self):
        return self._namespace.debug

    @property
    def disablePlugins(self):
        return self._namespace.disablePlugins

    def format_help(self):
        """Help string.

        Returns the help string."""
        return self._parser.format_help()
