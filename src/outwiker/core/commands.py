# -*- coding: utf-8 -*-

"""
Команды для интерфейса
"""

import logging
import os
import os.path
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union, Iterable

import wx

import outwiker.core.exceptions
from outwiker.api.core.images import isImage as _isImage
from outwiker.api.services.messages import showError
from outwiker.core.application import Application
from outwiker.core.attachment import Attachment
from outwiker.core.events import PostWikiOpenParams, PreWikiOpenParams
from outwiker.core.pagetitletester import PageTitleError, PageTitleWarning
from outwiker.core.system import getOS
from outwiker.core.tree import WikiDocument
from outwiker.core.tree_commands import getAlternativeTitle
from outwiker.gui.dateformatdialog import DateFormatDialog
from outwiker.gui.dialogs.overwritedialog import OverwriteDialog
from outwiker.gui.guiconfig import GeneralGuiConfig
from outwiker.gui.longprocessrunner import LongProcessRunner
from outwiker.gui.testeddialog import TestedFileDialog
from outwiker.gui.tester import Tester

# TODO: Remove in next version
from outwiker.api.core.tree import testreadonly
from outwiker.api.services.clipboard import copyTextToClipboard


logger = logging.getLogger('outwiker.core.commands')


def MessageBox(*args, **kwargs):
    """
    Замена стандартного MessageBox. Перед показом диалога отключает
    приложение от события EVT_ACTIVATE_APP.
    """
    result = Tester.dialogTester.runNext(None)
    if result is not None:
        return result

    wx.GetApp().unbindActivateApp()
    result = wx.MessageBox(*args, **kwargs)
    wx.GetApp().bindActivateApp()

    return result


@testreadonly
def renameAttach(parent: wx.Window,
                 page: 'outwiker.core.tree.WikiPage',
                 fname_src: str,
                 fname_dest: str) -> bool:
    """
    Rename attached file. Show overwrite dialog if necessary
    parent - parent for dialog window
    page - page to attach
    fname_src - source file name (relative path)
    fname_dest - new file name (relative path)

    Returns True if file renamed
    """
    if page.readonly:
        raise outwiker.core.exceptions.ReadonlyException

    attachRoot = Attachment(page).getAttachPath()
    fname_src_full = os.path.join(attachRoot, fname_src)
    fname_dest_full = os.path.join(attachRoot, fname_dest)

    if fname_src_full == fname_dest_full:
        return False

    if os.path.exists(fname_dest_full):
        with OverwriteDialog(parent) as overwriteDialog:
            overwriteDialog.setVisibleOverwriteAllButton(False)
            overwriteDialog.setVisibleSkipButton(False)
            overwriteDialog.setVisibleSkipAllButton(False)

            text = os.path.basename(fname_dest)
            try:
                src_file_stat = os.stat(fname_src_full)
                dest_file_stat = os.stat(fname_dest_full)
            except FileNotFoundError:
                return False
            result = overwriteDialog.ShowDialog(text,
                                                src_file_stat,
                                                dest_file_stat)

            if result == overwriteDialog.ID_SKIP or result == wx.ID_CANCEL:
                return False

    try:
        os.replace(fname_src_full, fname_dest_full)
    except (IOError, shutil.Error) as e:
        text = _('Error renaming file\n{} -> {}\n{}').format(fname_src, fname_dest, str(e))
        logger.error(text)
        showError(Application.mainWindow, text)
        return False

    return True


@testreadonly
def attachFiles(parent: wx.Window,
                page: 'outwiker.core.tree.WikiPage',
                files: List[str],
                subdir: str = '.'):
    """
    Attach files to page. Show overwrite dialog if necessary
    parent - parent for dialog window
    page - page to attach
    files - list of the files to attach
    subdir - subdirectory relative __attach directory
    """
    if page.readonly:
        raise outwiker.core.exceptions.ReadonlyException

    if not files:
        return

    def _expandFiles(files: Iterable[Union[str, Path]]) -> Iterable[Path]:
        """
        Returns list of all files (not directories) in subdirectories including
        """
        result = []
        for fname in files:
            item = Path(fname)
            if not item.exists():
                text = _('File not exists\n{0}').format(item)
                logger.error(text)
                showError(Application.mainWindow, text)
                return []

            if item.is_file():
                result.append(item)
            elif item.is_dir():
                files_inside = item.iterdir()
                result += _expandFiles(files_inside)

        return result

    def _getRelativeSubdirs(root: Path, expanded_files: Iterable[Union[str, Path]]) -> List[Path]:
        result = []
        for fname in expanded_files:
            path = Path(fname)
            parent = path.relative_to(root).parent
            if str(parent) != '.' and str(parent) != '/':
                result.append(parent)

        # Remove duplicates and sort directories alphabetically
        return sorted({item for item in result})

    attach = Attachment(page)
    attach_root = attach.getAttachPath(create=True)

    source_root_dir = Path(files[0]).parent
    expanded_files = _expandFiles(files)
    relative_source_files = [fname.relative_to(source_root_dir)
                             for fname in expanded_files]

    new_relative_attaches = []
    with OverwriteDialog(parent) as overwriteDialog:
        for fname_new in relative_source_files:
            old_path = Path(attach_root, subdir, fname_new)
            source_path = Path(source_root_dir, fname_new)

            if old_path == source_path:
                continue

            if old_path.exists():
                text = str(fname_new)
                old_file_stat = old_path.stat()
                new_file_stat = source_path.stat()

                result = overwriteDialog.ShowDialog(text,
                                                    old_file_stat,
                                                    new_file_stat)

                if result == overwriteDialog.ID_SKIP:
                    continue
                elif result == wx.ID_CANCEL:
                    return

            new_relative_attaches.append(fname_new)

    new_relative_subdirs = _getRelativeSubdirs(source_root_dir, expanded_files)

    for current_subdir in new_relative_subdirs:
        try:
            Path(attach_root, subdir, current_subdir).mkdir(parents=True, exist_ok=True)
        except IOError:
            text = _("Can't create directory: {}").format(current_subdir)
            logger.error(text)
            showError(Application.mainWindow, text)
            return

    for fname_relative in new_relative_attaches:
        source_full = Path(source_root_dir, fname_relative)
        attach_subdir = Path(attach_root, subdir, fname_relative.parent)
        try:
            Attachment(page).attach([source_full], attach_subdir)
        except (IOError, shutil.Error) as e:
            text = _('Error copying files\n{0}').format(str(e))
            logger.error(text)
            showError(Application.mainWindow, text)
            return


@testreadonly
def removePage(page: 'outwiker.core.tree.WikiPage'):
    assert page is not None

    if page.readonly:
        raise outwiker.core.exceptions.ReadonlyException

    if page.parent is None:
        showError(Application.mainWindow, _(
            "You can't remove the root element"))
        return

    if (MessageBox(_('Remove page "{}" and all subpages?\nAll attached files will also be deleted.').format(page.title),
                   _("Remove page?"),
                   wx.YES_NO | wx.ICON_QUESTION) == wx.YES):
        try:
            page.remove()
        except IOError:
            showError(Application.mainWindow, _("Can't remove page"))


def openWikiWithDialog(parent, readonly=False):
    """
    Показать диалог открытия вики и вернуть открытую wiki
    parent -- родительское окно
    """
    wikiroot = None

    with TestedFileDialog(parent,
                          wildcard="__page.opt|__page.opt",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
        if dialog.ShowModal() == wx.ID_OK:
            fullpath = dialog.GetPath()
            path = os.path.dirname(fullpath)
            wikiroot = openWiki(path, readonly)

    return wikiroot


def findPage(application, page_id):
    """
    page_id - subpath of page or page UID.
    """
    if application.wikiroot is None or page_id is None:
        return None

    prefix = 'page://'

    if page_id.startswith(prefix):
        page_id = page_id[len(prefix):]
        return application.pageUidDepot[page_id]
    elif application.wikiroot[page_id] is not None:
        return application.wikiroot[page_id]
    else:
        return application.pageUidDepot[page_id]


def openWiki(path: str, readonly: bool = False) -> Optional[WikiDocument]:
    def threadFunc(path, readonly):
        try:
            return WikiDocument.load(path, readonly)
        except Exception as e:
            return e

    logger.debug('Opening notes tree from: {}'.format(path))
    if not os.path.exists(path):
        _canNotLoadWikiMessage(path)
        return None

    preWikiOpenParams = PreWikiOpenParams(path, readonly)
    Application.onPreWikiOpen(Application.selectedPage,
                              preWikiOpenParams)
    if preWikiOpenParams.abortOpen:
        logger.debug('Opening notes tree aborted')
        return None

    # The path may be changed in event handlers
    path = preWikiOpenParams.path
    logger.debug('Notes tree path after onPreWikiOpen: {}'.format(path))

    # Если передан путь до файла настроек (а не до папки с вики),
    # то оставим только папку
    if not os.path.isdir(path):
        path = os.path.split(path)[0]

    runner = LongProcessRunner(threadFunc,
                               Application.mainWindow,
                               _(u"Loading"),
                               _(u"Opening notes tree..."))
    result = runner.run(os.path.realpath(path), readonly)

    success = False
    if isinstance(result, outwiker.core.exceptions.RootFormatError):
        _rootFormatErrorHandle(path, readonly)
    elif isinstance(result, Exception):
        logger.error(result)
        _canNotLoadWikiMessage(path)
    else:
        Application.wikiroot = result
        success = True

    postWikiOpenParams = PostWikiOpenParams(path, readonly, success)
    Application.onPostWikiOpen(Application.selectedPage,
                               postWikiOpenParams)

    return Application.wikiroot


def _rootFormatErrorHandle(path, readonly):
    """
    Обработчик исключения outwiker.core.exceptions.RootFormatError
    """
    if readonly:
        # Если вики открыт только для чтения, то нельзя изменять файлы
        _canNotLoadWikiMessage(path)
        return

    if (_wantClearWikiOptions(path) != wx.YES):
        return

    # Обнулим файл __page.opt
    WikiDocument.clearConfigFile(path)

    # Попробуем открыть вики еще раз
    try:
        # Загрузить вики
        wikiroot = WikiDocument.load(os.path.realpath(path), readonly)
        Application.wikiroot = wikiroot
    except IOError:
        _canNotLoadWikiMessage(path)

    except outwiker.core.exceptions.RootFormatError:
        _canNotLoadWikiMessage(path)

    finally:
        pass


def _canNotLoadWikiMessage(path):
    """
    Вывести сообщение о том, что невоможно открыть вики
    """
    logger.warning("Can't load notes tree: {}".format(path))
    text = _("Can't load notes tree:\n") + path
    showError(Application.mainWindow, text)


def _wantClearWikiOptions(path):
    """
    Сообщение о том, хочет ли пользователь сбросить файл __page.opt
    """
    return MessageBox(_("Can't load wiki '%s'\nFile __page.opt is invalid.\nClear this file and load wiki?\nBookmarks will be lost") % path,
                      _("__page.opt error"),
                      wx.ICON_ERROR | wx.YES_NO)


def createNewWiki(parentwnd):
    """
    Создать новую вики
    parentwnd - окно-владелец диалога выбора файла
    """
    newPageTitle = _("First Wiki Page")
    newPageContent = _("""!! First Wiki Page

This is the first page. You can use a text formatting: '''bold''', ''italic'', {+underlined text+}, [[https://jenyay.net | link]] and others.""")

    with TestedFileDialog(parentwnd, style=wx.FD_SAVE) as dlg:
        dlg.SetDirectory(getOS().documentsDir)

        if dlg.ShowModal() == wx.ID_OK:
            try:
                from outwiker.pages.wiki.wikipage import WikiPageFactory

                newwiki = WikiDocument.create(dlg.GetPath())
                WikiPageFactory().create(newwiki, newPageTitle, [_("test")])
                firstPage = newwiki[newPageTitle]
                firstPage.content = newPageContent

                Application.wikiroot = newwiki
                Application.wikiroot.selectedPage = firstPage
            except (IOError, OSError) as e:
                # TODO: проверить под Windows
                showError(Application.mainWindow, _(
                    "Can't create wiki\n") + e.filename)


@testreadonly
def movePage(page, newParent):
    """
    Сделать страницу page ребенком newParent
    """
    assert page is not None
    assert newParent is not None

    try:
        page.moveTo(newParent)
    except outwiker.core.exceptions.DuplicateTitle:
        # Невозможно переместить из-за дублирования имен
        showError(Application.mainWindow, _(
            u"Can't move page when page with that title already exists"))
    except outwiker.core.exceptions.TreeException:
        # Невозможно переместить по другой причине
        showError(Application.mainWindow, _(
            u"Can't move page: {}".format(page.display_title)))


def addStatusBarItem(name: str, width: int = -1, position: Optional[int] = None) -> None:
    if Application.mainWindow:
        Application.mainWindow.statusbar.addItem(name, width, position)


def setStatusText(item_name: str, text: str) -> None:
    """
    Установить текст статусбара.
    text - текст
    index - номер ячейки статусбара
    """
    if Application.mainWindow:
        Application.mainWindow.statusbar.setStatusText(item_name, text)


@testreadonly
def renamePage(page, newtitle):
    if page.parent is None:
        showError(Application.mainWindow, _(
            u"You can't rename the root element"))
        return

    newtitle = newtitle.strip()

    if newtitle == page.display_title:
        return

    siblings = [child.title
                for child in page.parent.children
                if child != page]

    real_title = getAlternativeTitle(newtitle, siblings)

    try:
        page.title = real_title
    except OSError:
        showError(Application.mainWindow,
                  _('Can\'t rename page "{}" to "{}"').format(page.display_title, newtitle))

    if real_title != newtitle:
        page.alias = newtitle
    else:
        page.alias = None


def testPageTitle(title):
    """
    Возвращает True, если можно создавать страницу с таким заголовком
    """
    tester = getOS().pageTitleTester

    try:
        tester.test(title)

    except PageTitleError as error:
        MessageBox(str(error),
                   _("Invalid page title"),
                   wx.OK | wx.ICON_ERROR)
        return False

    except PageTitleWarning as warning:
        text = _("{0}\nContinue?").format(str(warning))

        if (MessageBox(text,
                       _("The page title"),
                       wx.YES_NO | wx.ICON_QUESTION) == wx.YES):
            return True
        else:
            return False

    return True


def getMainWindowTitle(application):
    template = application.mainWindow.mainWindowConfig.titleFormat.value

    if application.wikiroot is None:
        result = "OutWiker"
    else:
        page = application.wikiroot.selectedPage

        pageTitle = u"" if page is None else page.display_title
        subpath = u"" if page is None else page.display_subpath
        filename = os.path.basename(application.wikiroot.path)

        result = (template
                  .replace("{file}", filename)
                  .replace("{page}", pageTitle)
                  .replace("{subpath}", subpath)
                  )

    return result


def insertCurrentDate(parent, editor):
    """
    Вызвать диалог для выбора формата даты и вставить в редактор текущую дату согласно выбранному формату.

    parent - родительское окно для диалога
    editor - текстовое поле ввода, куда надо вставить дату (экземпляр класса TextEditor)
    """
    config = GeneralGuiConfig(Application.config)
    initial = config.recentDateTimeFormat.value

    with DateFormatDialog(parent,
                          _("Enter format of the date"),
                          _("Date format"),
                          initial) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            dateStr = datetime.now().strftime(dlg.Value)
            editor.replaceText(dateStr)
            config.recentDateTimeFormat.value = dlg.Value


# TODO: Remove in next version
def isImage(fname: Union[Path, str]) -> bool:
    """
    Depricated. Use outwiker.core.images.isImage()
    """
    return _isImage(fname)
