#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os.path

from outwiker.core.pluginbase import Plugin
from outwiker.core.system import getOS

from .controller import Controller
from .exporterfactory import ExporterFactory
from .branchexporter import BranchExporter

# from .i18n import _
import i18n


class PluginExport2Html (Plugin):
    def __init__ (self, application):
        """
        application - экземпляр класса core.application.ApplicationParams
        """
        Plugin.__init__ (self, application)
        self.__controller = Controller (self, application)


    @property
    def application (self):
        return self._application


    ###################################################
    # Свойства и методы, которые необходимо определить
    ###################################################

    @property
    def name (self):
        return u"Export to HTML"

    
    @property
    def description (self):
        return _(u"Export pages to HTML")


    @property
    def version (self):
        return u"1.0"

    
    def initialize(self):
        self.__initlocale()
        self.__controller.initialize ()


    def destroy (self):
        """
        Уничтожение (выгрузка) плагина. Здесь плагин должен отписаться от всех событий
        """
        self.__controller.destroy()

    #############################################

    def __initlocale (self):
        domain = u"export2html"

        langdir = unicode (os.path.join (os.path.dirname (__file__), "locale"), getOS().filesEncoding)
        global _

        try:
            _ = self._init_i18n (domain, langdir)
            # print _
        except BaseException as e:
            print e


    @property
    def exporterFactory (self):
        """
        Возвращает класс Exporter, чтобы его можно было легче тестировать при загрузке плагина в реальном времени
        """
        return ExporterFactory


    @property
    def branchExporter (self):
        return BranchExporter
