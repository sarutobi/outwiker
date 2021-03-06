# -*- coding: utf-8 -*-

import wx
import wx.aui

from outwiker.gui.toolbars.basetoolbar import BaseToolBar


class LatexToolBar (BaseToolBar):
    def __init__ (self, parent, auiManager):
        super (LatexToolBar, self).__init__(parent, auiManager)


    def _createPane (self):
        return wx.aui.AuiPaneInfo().Name(self.name).Caption(self.caption).ToolbarPane().Top().Position(10)


    @property
    def name (self):
        return u"latexToolBar"


    @property
    def caption (self):
        return _(u"LaTeX")
