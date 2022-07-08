# -*- coding=utf-8 -*-

import wx
from wx.adv import RichToolTip


class ControlNotify:
    def __init__(self, control: wx.Window):
        self._control = control

    def ShowError(self, title, text):
        tooltip = RichToolTip(title, text)
        tooltip.SetIcon(wx.ICON_ERROR)
        tooltip.SetBackgroundColour("#F6D1C8", "#F6D1C8")
        tooltip.ShowFor(self._control)
