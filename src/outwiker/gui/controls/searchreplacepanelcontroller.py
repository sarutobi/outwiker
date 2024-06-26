# -*- coding: utf-8 -*-

import wx

from outwiker.gui.controls.searchreplacepanel import SearchReplacePanel


class SearchReplacePanelController:
    _recentSearch = ''

    def __init__(self, searchPanel: SearchReplacePanel, editor):
        """
        searchPanel - панель со строкой поиска
        editor - текстовый редактор (экземпляр класса TextEditor)
        """
        # Панель со строкой поиска
        self.panel = searchPanel
        self.editor = editor

        self._searcher = LocalSearcher()

        self.setSearchPhrase(SearchReplacePanelController._recentSearch)
        self._bindGui(self.panel)

    def _bindGui(self, panel):
        panel.Bind(wx.EVT_CLOSE, self._onClose)
        panel.Bind(wx.EVT_TEXT_ENTER, self._onEnterPress, panel.getSearchTextCtrl())
        panel.Bind(wx.EVT_TEXT_ENTER, self._onEnterPress, panel.getReplaceTextCtrl())
        panel.Bind(wx.EVT_TEXT, self._onSearchTextChange, panel.getSearchTextCtrl())
        panel.Bind(wx.EVT_BUTTON, self._onNextSearch, panel.getNextSearchBtn())
        panel.Bind(wx.EVT_BUTTON, self._onPrevSearch, panel.getPrevSearchBtn())
        panel.Bind(wx.EVT_BUTTON, self._onReplace, panel.getReplaceBtn())
        panel.Bind(wx.EVT_BUTTON, self._onReplaceAll, panel.getReplaceAllBtn())
        panel.Bind(wx.EVT_BUTTON, self._onCloseClick, panel.getCloseBtn())

    def _onEnterPress(self, _event):
        if self.panel.getReplaceTextCtrl.IsShown():
            self.replace()
        else:
            self.nextSearch()

    def _onReplaceAll(self, _event):
        self.replaceAll()

    def _onReplace(self, _event):
        self.replace()

    def _onPrevSearch(self, _event):
        self.prevSearch()

    def _onNextSearch(self, _event):
        self.nextSearch()

    def _onSearchTextChange(self, _event):
        self.enterSearchPhrase()

    def _onCloseClick(self, _event):
        self.panel.Close()

    def _onClose(self, _event):
        self.editor.SetFocus()
        self.panel.Hide()
        self.panel.GetParent().Layout()

    def nextSearch(self):
        """
        Искать следующее вхождение фразы
        """
        self._searchTo(self._findNext)
        if self.getSearchPhrase():
            self.editor.SetFocus()

    def prevSearch(self):
        """
        Искать предыдущее вхождение фразы
        """
        self._searchTo(self._findPrev)
        if self.getSearchPhrase():
            self.editor.SetFocus()

    def replace(self):
        """
        Сделать замену
        Возвращает True, если удалось сделать замену
        """
        phrase = self.getSearchPhrase()
        searchResult = SearchResult(self.editor.GetSelectionStart(),
                                    self.editor.GetSelectedText())

        if (len(phrase) > 0 and self._searcher.inResult(searchResult)):
            self.editor.replaceText(self.getReplacePhrase())
            self.nextSearch()
            return True

        return False

    def replaceAll(self):
        """
        Заменить все
        """
        phrase = self.getSearchPhrase()
        if len(phrase) == 0:
            return

        text = self.editor.GetText()
        self._searcher.search(text, phrase)

        if len(self._searcher.result) == 0:
            return

        replace = self.getReplacePhrase()

        newtext = ""
        position = 0

        for currResult in self._searcher.result:
            newtext += text[position: currResult.position]
            newtext += replace
            position = currResult.position + len(currResult.phrase)

        # Место окончания последней замены (чтобы туда поставить курсор)
        lastreplace = len(newtext)

        newtext += text[position:]

        self.editor.SetText(newtext)
        self.editor.SetSelection(lastreplace, lastreplace)
        self.editor.SetFocus()

    def startSearch(self):
        """
        Начать поиск
        """
        phrase = self.editor.GetSelectedText()

        if len(phrase) == 0:
            phrase = SearchReplacePanelController._recentSearch
            self.setSearchPhrase(phrase)

        self.setSearchPhrase(phrase)
        self.panel.getSearchTextCtrl().SetSelection(-1, -1)
        self.panel.getSearchTextCtrl().SetFocus()

    def enterSearchPhrase(self):
        self._searchTo(self._findNextOnEnter)

    def show(self):
        if not self.panel.IsShown():
            self.panel.Show()
            self.panel.Fit()
            self.panel.GetParent().Layout()

    def setSearchPhrase(self, phrase):
        """
        В панели поиска установить искомую фразу.
        При этом сразу начинается поиск
        """
        self.panel.getSearchTextCtrl().SetValue(phrase)

    def getSearchPhrase(self):
        """
        Возвращает искомую фразу из панели
        """
        return self.panel.getSearchTextCtrl().GetValue()

    def setReplacePhrase(self, phrase):
        self.panel.getReplaceTextCtrl().SetValue(phrase)

    def getReplacePhrase(self):
        return self.panel.getReplaceTextCtrl().GetValue()

    def switchToSearchMode(self):
        """
        Переключиться в режим поиска
        """
        self.panel.Close()
        self.panel.setReplaceGuiVisible(False)
        self.show()

    def switchToReplaceMode(self):
        """
        Переключиться в режим поиска
        """
        self.panel.Close()
        # Если редактор находится в режиме "только для чтения",
        # то не показывать GUI предназначенный для замены
        self.panel.setReplaceGuiVisible(not self.editor.GetReadOnly())
        self.show()

    def _searchTo(self, direction):
        """
        Поиск фразы в нужном направлении (вперед / назад)
        direction - функция, которая ищет текст в нужном направлении
            (_findNext / _findPrev)
        """
        self.panel.getSearchTextCtrl().SetFocus()
        phrase = self.getSearchPhrase()

        SearchReplacePanelController._recentSearch = phrase

        if len(phrase) == 0:
            return

        text = self.editor.GetText()
        result = direction(text, phrase)
        if result is not None:
            self.panel.getResultLabel().SetLabel("")
            self.editor.GotoPos(result.position)
            self.editor.SetSelection(result.position,
                                     result.position + len(result.phrase))
        else:
            self.panel.getResultLabel().SetLabel(_("Not found"))

        self.panel.Layout()

    def _findNext(self, text, phrase):
        """
        Найти следующее вхождение
        """
        self._searcher.search(text, phrase)

        currpos = self.editor.GetCurrentPosition()

        result = None

        for currResult in self._searcher.result:
            if currResult.position >= currpos:
                result = currResult
                break

        if result is None and len(self._searcher.result) > 0:
            result = self._searcher.result[0]

        return result

    def _findPrev(self, text, phrase):
        """
        Найти предыдущее вхождение
        """
        self._searcher.search(text, phrase)

        currpos = self.editor.GetSelectionStart()

        result = None

        for currResult in self._searcher.result:
            if currResult.position < currpos:
                result = currResult

        if result is None and len(self._searcher.result) > 0:
            result = self._searcher.result[-1]

        return result

    def _findNextOnEnter(self, text, phrase):
        """
        Найти следующее вхождение, но начиная с начала выделения текста
        """
        self._searcher.search(text, phrase)

        currpos = self.editor.GetSelectionStart()

        result = None

        for currResult in self._searcher.result:
            if currResult.position >= currpos:
                result = currResult
                break

        if result is None and len(self._searcher.result) > 0:
            result = self._searcher.result[0]

        return result


class SearchResult(object):
    """
    Результат поиска по странице
    """
    def __init__(self, position, phrase):
        """
        position - начало найденного текста
        """
        self.position = position
        self.phrase = phrase


class LocalSearcher(object):
    """
    Класс для поиска по странице
    """
    def __init__(self):
        self._result = []

    @property
    def result(self):
        return self._result

    def search(self, text, phrase):
        self._result = []

        text_lower = text.lower()
        phrase_lower = phrase.lower()

        index = text_lower.find(phrase_lower)

        while index != -1:
            self._result.append(SearchResult(index, phrase_lower))
            index = text_lower.find(phrase_lower, index + len(phrase_lower))

    def inResult(self, testResult):
        """
        testResult - экземпляр класса SearchResult
        Функция возвращает True, если в self._result есть результат поиска,
        соответствующий testResult

        Эта функция используется для того, чтобы проверять выделенный в
        редакторе фрагмент на соответствие поисковой фразе
        """
        for resultItem in self._result:
            if (testResult.position == resultItem.position and
                    testResult.phrase.lower() == resultItem.phrase.lower()):
                return True

        return False
