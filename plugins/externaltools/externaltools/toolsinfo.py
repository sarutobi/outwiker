# -*- coding: utf-8 -*-


class ToolsInfo:
    """
    Информация о каждом вызываемом внешнем редакторе
    """

    def __init__(self, command, title, toolsid):
        self.command = command
        self.title = title
        self.toolsid = toolsid
