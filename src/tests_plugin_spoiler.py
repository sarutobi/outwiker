#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Unit-тесты
"""

import os
from outwiker.core.defines import WX_VERSION

import wxversion

try:
    wxversion.select(WX_VERSION)
except wxversion.VersionError:
    if os.name == "nt":
        pass
    else:
        raise

import wx


if __name__ == '__main__':
    from outwiker.core.application import Application
    Application.init("../test/testconfig.ini")

    app = wx.App(redirect=False)

    def emptyFunc():
        pass

    app.bindActivateApp = emptyFunc
    app.unbindActivateApp = emptyFunc
    loop = wx.EventLoop()
    wx.EventLoop.SetActive(loop)
    wx.Log.SetLogLevel(0)

    import unittest

    from test.plugins.spoiler.test_loading import SpoilerLoadingTest
    from test.plugins.spoiler.test_spoiler import SpoilerPluginTest

    unittest.main()
