# -*- coding: utf-8 -*-

import os.path
from typing import List

import wx

from outwiker.actions.attachexecute import AttachExecuteFilesAction
from outwiker.actions.attachfiles import AttachFilesActionForAttachPanel
from outwiker.actions.attachopenfolder import (OpenAttachFolderAction,
                                               OpenAttachFolderActionForAttachPanel)
from outwiker.actions.attachpastelink import AttachPasteLinkActionForAttachPanel
from outwiker.actions.attachremove import RemoveAttachesActionForAttachPanel
from outwiker.actions.attachselectall import AttachSelectAllAction
from outwiker.core.attachment import Attachment
from outwiker.core.commands import MessageBox, attachFiles, showError
from outwiker.core.system import getBuiltinImagePath, getOS

from .dropfiles import BaseDropFilesTarget
from .guiconfig import AttachConfig


class AttachPanel(wx.Panel):
    def __init__(self, parent, application):
        super().__init__(parent)
        self._application = application

        self.__attachList = wx.ListCtrl(self,
                                        wx.ID_ANY,
                                        style=wx.LC_LIST | wx.SUNKEN_BORDER)

        self.__toolbar = self.__createGui(self)
        self.__attachList.SetMinSize((-1, 100))
        self.__do_layout()

        self.__fileIcons = getOS().fileIcons
        self.__attachList.SetImageList(self.__fileIcons.imageList,
                                       wx.IMAGE_LIST_SMALL)
        self._dropTarget = DropAttachFilesTarget(self._application, self)

        self.__bindGuiEvents()
        self.__bindAppEvents()

    def SetBackgroundColour(self, colour):
        super().SetBackgroundColour(colour)
        self.__attachList.SetBackgroundColour(colour)

    def SetForegroundColour(self, colour):
        super().SetForegroundColour(colour)
        self.__attachList.SetForegroundColour(colour)

    def __bindGuiEvents(self):
        self.Bind(wx.EVT_LIST_BEGIN_DRAG,
                  self.__onBeginDrag, self.__attachList)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__onDoubleClick,
                  self.__attachList)

        self.Bind(wx.EVT_CLOSE, self.__onClose)

    def __unbindGuiEvents(self):
        self.Unbind(wx.EVT_LIST_BEGIN_DRAG,
                    handler=self.__onBeginDrag,
                    source=self.__attachList)

        self.Unbind(wx.EVT_LIST_ITEM_ACTIVATED,
                    handler=self.__onDoubleClick,
                    source=self.__attachList)

        self.Unbind(wx.EVT_CLOSE, handler=self.__onClose)

    @property
    def attachList(self):
        return self.__attachList

    @property
    def toolBar(self):
        return self.__toolbar

    def __bindAppEvents(self):
        self._application.onPageSelect += self.__onPageSelect
        self._application.onAttachListChanged += self.__onAttachListChanged
        self._application.onWikiOpen += self.__onWikiOpen

    def __unbindAppEvents(self):
        self._application.onPageSelect -= self.__onPageSelect
        self._application.onAttachListChanged -= self.__onAttachListChanged
        self._application.onWikiOpen -= self.__onWikiOpen

    def __onClose(self, _event):
        actionController = self._application.actionController

        for action, hotkey, hidden in self._actions:
            actionController.removeHotkey(action.stringId)
            actionController.removeToolbarButton(action.stringId)

        self._dropTarget.destroy()
        self.__unbindAppEvents()
        self.__unbindGuiEvents()
        self.toolBar.ClearTools()
        self.attachList.ClearAll()
        self.__fileIcons.clear()
        self.Destroy()

    def __createGui(self, parent):
        toolbar = wx.ToolBar(parent, wx.ID_ANY, style=wx.TB_DOCKABLE)
        actionController = self._application.actionController

        # Attach files
        actionController.appendToolbarButton(
            AttachFilesActionForAttachPanel.stringId,
            toolbar,
            getBuiltinImagePath("attach.png")
        )

        # Delete files
        actionController.appendToolbarButton(
            RemoveAttachesActionForAttachPanel.stringId,
            toolbar,
            getBuiltinImagePath("delete.png")
        )

        actionController.appendHotkey(
            RemoveAttachesActionForAttachPanel.stringId,
            self)

        # Select all files
        actionController.appendToolbarButton(
            AttachSelectAllAction.stringId,
            toolbar,
            getBuiltinImagePath("select_all.png")
        )

        actionController.appendHotkey(
            AttachSelectAllAction.stringId,
            self)

        toolbar.AddSeparator()

        # Paste link to files
        actionController.appendToolbarButton(
            AttachPasteLinkActionForAttachPanel.stringId,
            toolbar,
            getBuiltinImagePath("paste.png")
        )

        actionController.appendHotkey(
            AttachPasteLinkActionForAttachPanel.stringId,
            self)

        # Execute files
        actionController.appendToolbarButton(
            AttachExecuteFilesAction.stringId,
            toolbar,
            getBuiltinImagePath("execute.png")
        )

        actionController.appendHotkey(
            AttachExecuteFilesAction.stringId,
            self)

        # Open attach folder
        actionController.appendToolbarButton(
            OpenAttachFolderActionForAttachPanel.stringId,
            toolbar,
            getBuiltinImagePath("folder.png")
        )

        toolbar.Realize()
        return toolbar

    def __do_layout(self):
        attachSizer_copy = wx.FlexGridSizer(2, 1, 0, 0)
        attachSizer_copy.Add(self.__toolbar, 1, wx.EXPAND, 0)
        attachSizer_copy.Add(self.__attachList, 1, wx.ALL | wx.EXPAND, 2)
        self.SetSizer(attachSizer_copy)
        attachSizer_copy.Fit(self)
        attachSizer_copy.AddGrowableRow(1)
        attachSizer_copy.AddGrowableCol(0)

        attachSizer_copy.Fit(self)
        self.SetAutoLayout(True)

    def __onWikiOpen(self, _wiki):
        self.updateAttachments()

    def __onPageSelect(self, _page):
        self.updateAttachments()

    def __sortFilesList(self, files_list):
        result = sorted(files_list, key=str.lower, reverse=True)
        result.sort(key=Attachment.sortByType)
        return result

    def updateAttachments(self):
        """
        Обновить список прикрепленных файлов
        """
        self.__attachList.Freeze()
        self.__attachList.ClearAll()
        if self._application.selectedPage is not None:
            files = Attachment(self._application.selectedPage).attachmentFull
            files = self.__sortFilesList(files)

            for fname in files:
                if (not os.path.basename(fname).startswith("__") or
                        not os.path.isdir(fname)):
                    # Отключим уведомления об ошибках во всплывающих окнах
                    # иначе они появляются при попытке прочитать
                    # испорченные иконки
                    # На результат работы это не сказывается,
                    # все-равно бракованные иконки отлавливаются.
                    wx.Log.EnableLogging(False)

                    imageIndex = self.__fileIcons.getFileImage(fname)

                    # Вернем всплывающие окна с ошибками
                    wx.Log.EnableLogging(True)

                    self.__attachList.InsertItem(
                        0,
                        os.path.basename(fname),
                        imageIndex)

        self.__attachList.Thaw()

    def getSelectedFiles(self):
        files = []

        item = self.__attachList.GetNextItem(-1, state=wx.LIST_STATE_SELECTED)

        while item != -1:
            fname = self.__attachList.GetItemText(item)
            files.append(fname)

            item = self.__attachList.GetNextItem(item,
                                                 state=wx.LIST_STATE_SELECTED)

        return files

    def __onRemove(self, _event):
        if self._application.selectedPage is not None:
            files = self.getSelectedFiles()

            if len(files) == 0:
                showError(self._application.mainWindow,
                          _("You did not select any file to remove"))
                return

            if MessageBox(_("Remove selected files?"),
                          _("Remove files?"),
                          wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                try:
                    Attachment(
                        self._application.selectedPage).removeAttach(files)
                except IOError as e:
                    showError(self._application.mainWindow, str(e))

                self.updateAttachments()

    def __onDoubleClick(self, _event):
        config = AttachConfig(self._application.config)
        actionController = self._application.actionController

        if config.doubleClickAction.value == AttachConfig.ACTION_INSERT_LINK:
            actionController.getAction(
                AttachPasteLinkActionForAttachPanel.stringId).run(None)
        elif config.doubleClickAction.value == AttachConfig.ACTION_OPEN:
            actionController.getAction(
                AttachExecuteFilesAction.stringId).run(None)

    def __onBeginDrag(self, _event):
        selectedFiles = self.getSelectedFiles()
        if not selectedFiles:
            return

        data = wx.FileDataObject()
        attach_path = Attachment(
            self._application.selectedPage).getAttachPath()

        for fname in self.getSelectedFiles():
            data.AddFile(os.path.join(attach_path, fname))

        dragSource = wx.DropSource(data, self)
        dragSource.DoDragDrop()

    def __onAttachListChanged(self, page, _params):
        if page is not None and page == self._application.selectedPage:
            self.updateAttachments()

    def SetFocus(self):
        self.__attachList.SetFocus()

        if (self.__attachList.GetItemCount() != 0 and
                self.__attachList.GetFocusedItem() == -1):
            self.__attachList.Focus(0)
            self.__attachList.Select(0)

    def selectAllAttachments(self):
        for index in range(self.__attachList.GetItemCount()):
            self.__attachList.SetItemState(index,
                                           wx.LIST_STATE_SELECTED,
                                           wx.LIST_STATE_SELECTED)


class DropAttachFilesTarget(BaseDropFilesTarget):
    """
    Класс для возможности перетаскивания файлов
    между другими программами и панелью с прикрепленными файлами.
    """

    def OnDropFiles(self, x: int, y: int, files: List[str]) -> bool:
        correctedFiles = self.correctFileNames(files)

        if (self._application.wikiroot is not None and
                self._application.wikiroot.selectedPage is not None):
            attachFiles(self._application.mainWindow,
                        self._application.wikiroot.selectedPage,
                        correctedFiles)
            return True

        return False
