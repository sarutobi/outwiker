# -*- coding=utf-8 -*-

import os.path

from outwiker.core.attachment import Attachment
from outwiker.core.commands import showError
from outwiker.core.system import getOS
from outwiker.gui.baseaction import BaseAction


class AttachSelectAllAction(BaseAction):
    """
    Select all attached files on attachments panel
    """
    stringId = "AttachSelectAll"

    def __init__(self, application):
        self._application = application

    @property
    def title(self):
        return _("Select all")

    @property
    def description(self):
        return _("Select all attached files. Action for attachments panel")

    def run(self, params):
        self._application.mainWindow.attachPanel.panel.selectAllAttachments()
