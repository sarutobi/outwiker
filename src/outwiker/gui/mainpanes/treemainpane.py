# -*- coding: UTF-8 -*-

import wx.aui

from .mainpane import MainPane
from outwiker.gui.guiconfig import TreeConfig
from outwiker.gui.notestree import NotesTree


class TreeMainPane (MainPane):
    def beginRename (self, page=None):
        self.panel.beginRename(page)


    def _createPanel (self):
        return NotesTree (self.parent, -1)


    def _createConfig (self):
        return TreeConfig (self.application.config)


    @property
    def caption(self):
        return _(u"Notes")


    def _createPane (self):
        pane = self._loadPaneInfo (self.config.pane)

        if pane is None:
            pane = wx.aui.AuiPaneInfo().Name("treePane").Caption(self.caption).Gripper(False).CaptionVisible(True).Layer(2).Position(0).CloseButton(True).MaximizeButton(False).Left().Dock()

        # Из-за глюка http://trac.wxwidgets.org/ticket/12422 придется пока отказаться от плавающих панелек
        pane.Dock()
        pane.CloseButton()
        pane.Caption(self.caption)

        pane.BestSize((self.config.width.value,
                       self.config.height.value))

        return pane
