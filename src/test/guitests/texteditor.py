#!/usr/bin/python
# -*- coding: UTF-8 -*-

from basemainwnd import BaseMainWndTest
from outwiker.core.tree import WikiDocument
from outwiker.core.application import Application
from outwiker.pages.text.textpage import TextPageFactory
from test.utils import removeWiki

class TextEditorTest (BaseMainWndTest):
    """
    Тесты действий для викистраницы
    """
    def setUp (self):
        BaseMainWndTest.setUp (self)

        self.path = u"../test/testwiki"
        removeWiki (self.path)

        self.wikiroot = WikiDocument.create (self.path)
        TextPageFactory.create (self.wikiroot, u"Страница", [])

        self.testpage = self.wikiroot[u"Страница"]

        Application.wikiroot = self.wikiroot
        Application.selectedPage = self.testpage


    def tearDown (self):
        BaseMainWndTest.tearDown (self)
        Application.wikiroot = None
        removeWiki (self.path)


    def _getEditor (self):
        return Application.mainWindow.pagePanel.pageView.textEditor


    def testGetSetText (self):
        sourceText = u"000 Проверка 111"

        self._getEditor().SetText (sourceText)

        text = self._getEditor().GetText()

        self.assertEqual (text, sourceText)
        self.assertEqual (text[:10], sourceText[:10])


    def testGetTextEmpty (self):
        self.assertEqual (len (self._getEditor().GetText()), 0)


    def testAddText (self):
        self._getEditor().AddText(u"Абырвалг")
        self.assertEqual (self._getEditor().GetText(), u"Абырвалг")

        self._getEditor().AddText(u"\nРаз два три")
        self.assertEqual (self._getEditor().GetText(), u"Абырвалг\nРаз два три")


    def testGetSelectionEmpty (self):
        selText = self._getEditor().GetSelectedText()
        self.assertEqual (len (self._getEditor().GetText()), 0)


    def testSelection (self):
        text = u"""Абырвалг 
проверка
раз два три 
четыре
"""
        self._getEditor().SetText (text)
        self.assertEqual (len (self._getEditor().GetSelectedText() ), 0)

        self._getEditor().SetSelection (0, 0)
        self.assertEqual (len (self._getEditor().GetSelectedText() ), 0)

        self._getEditor().SetSelection (0, 1)
        self.assertEqual (self._getEditor().GetSelectedText(), u"А")

        self._getEditor().SetSelection (0, -1)
        self.assertEqual (self._getEditor().GetSelectedText(), text[0: -1])

        self._getEditor().SetSelection (0, len (text))
        self.assertEqual (self._getEditor().GetSelectedText(), text)

        self._getEditor().SetSelection (11, 16)
        self.assertEqual (self._getEditor().GetSelectedText(), text[11: 16])


    def testReplaceText (self):
        text = u"""Абырвалг 
проверка
раз два три 
четыре
"""

        # Замена при пустом тексте
        self._getEditor().replaceText (u"Абырвалг")
        self.assertEqual (self._getEditor().GetText(), u"Абырвалг")

        self._getEditor().SetText (text)
        self._getEditor().replaceText (u"Абырвалг")
        self.assertEqual (self._getEditor().GetText(), u"""АбырвалгАбырвалг 
проверка
раз два три 
четыре
""")

        self._getEditor().SetText (text)
        self._getEditor().SetSelection (0, 3)
        self._getEditor().replaceText (u"Замена")
        self.assertEqual (self._getEditor().GetText(), u"""Заменарвалг 
проверка
раз два три 
четыре
""")

        self._getEditor().SetText (text)
        self._getEditor().SetSelection (1, 5)
        self._getEditor().replaceText (u"Замена")
        self.assertEqual (self._getEditor().GetText(), u"""АЗаменаалг 
проверка
раз два три 
четыре
""")


    def testEscapeHtmlEmpty (self):
        self._getEditor().escapeHtml()
        self.assertEqual (len (self._getEditor().GetText() ), 0)


    def testEscapeHtml (self):
        text = u"Проверка > тест < 1234"

        self._getEditor().SetText (text)
        self._getEditor().escapeHtml()
        self.assertEqual (self._getEditor().GetText(), text)

        self._getEditor().SetText (text)
        self._getEditor().SetSelection (0, 10)
        self._getEditor().escapeHtml()
        self.assertEqual (self._getEditor().GetText(), u"Проверка &gt; тест < 1234")

        self._getEditor().SetText (text)
        self._getEditor().SetSelection (0, -1)
        self._getEditor().escapeHtml()
        self.assertEqual (self._getEditor().GetText(), u"Проверка &gt; тест &lt; 1234")


    def testTurnTextEmpty (self):
        self._getEditor().turnText (u"Лево", u"Право")
        self.assertEqual (self._getEditor().GetText(), u"ЛевоПраво")


    def testTurnText (self):
        text = u"Проверка абырвалг"

        self._getEditor().SetText (text)
        self._getEditor().SetSelection (0, 1)
        self._getEditor().turnText (u"Лево", u"Право")
        self.assertEqual (self._getEditor().GetText(), u"ЛевоППравороверка абырвалг")

        self._getEditor().SetText (text)
        self._getEditor().SetSelection (1, 3)
        self._getEditor().turnText (u"Лево", u"Право")
        self.assertEqual (self._getEditor().GetText(), u"ПЛевороПравоверка абырвалг")

        self._getEditor().SetText (text)
        self._getEditor().SetSelection (0, len (text))
        self._getEditor().turnText (u"Лево", u"Право")
        self.assertEqual (self._getEditor().GetText(), u"ЛевоПроверка абырвалгПраво")


    def testGetCurrentPositionEmpty (self):
        self.assertEqual (self._getEditor().GetCurrentPosition(), 0)


    def testGetCurrentPosition (self):
        text = u"Проверка абырвалг"
        self._getEditor().SetText (text)

        self._getEditor().SetSelection (0, 1)
        self.assertEqual (self._getEditor().GetCurrentPosition(), 1)

        self._getEditor().SetSelection (1, 0)
        self.assertEqual (self._getEditor().GetCurrentPosition(), 0)

        self._getEditor().SetSelection (10, 10)
        self.assertEqual (self._getEditor().GetCurrentPosition(), 10)


    def testGetSelectionPosEmpty (self):
        self.assertEqual (self._getEditor().GetSelectionStart(), 0)
        self.assertEqual (self._getEditor().GetSelectionEnd(), 0)


    def testGetSelectionPos (self):
        text = u"Проверка абырвалг"
        self._getEditor().SetText (text)

        self._getEditor().SetSelection (0, 0)
        self.assertEqual (self._getEditor().GetSelectionStart(), 0)
        self.assertEqual (self._getEditor().GetSelectionEnd(), 0)

        self._getEditor().SetSelection (0, 1)
        self.assertEqual (self._getEditor().GetSelectionStart(), 0)
        self.assertEqual (self._getEditor().GetSelectionEnd(), 1)

        self._getEditor().SetSelection (1, 0)
        self.assertEqual (self._getEditor().GetSelectionStart(), 0)
        self.assertEqual (self._getEditor().GetSelectionEnd(), 1)

        self._getEditor().SetSelection (10, 10)
        self.assertEqual (self._getEditor().GetSelectionStart(), 10)
        self.assertEqual (self._getEditor().GetSelectionEnd(), 10)

        self._getEditor().SetSelection (0, len (text))
        self.assertEqual (self._getEditor().GetSelectionStart(), 0)
        self.assertEqual (self._getEditor().GetSelectionEnd(), len (text))
        self.assertEqual (self._getEditor().GetSelectedText(), text)


    def testGetSetSearchPhrase (self):
        searchController = self._getEditor().searchPanel

        searchController.setSearchPhrase (u"Абырвалг")
        self.assertEqual (searchController.getSearchPhrase(), u"Абырвалг")


    def testSearchNext (self):
        editor = self._getEditor()
        editor.SetText (u"Абырвалг проверка абырвалг")
        editor.SetSelection (0, 0)

        searchController = editor.searchPanel

        searchController.setSearchPhrase (u"абырвалг")
        self.assertEqual (editor.GetSelectionStart(), 0)
        self.assertEqual (editor.GetSelectionEnd(), 8)

        searchController.nextSearch()
        self.assertEqual (editor.GetSelectionStart(), 18)
        self.assertEqual (editor.GetSelectionEnd(), 26)

        searchController.nextSearch()
        self.assertEqual (editor.GetSelectionStart(), 0)
        self.assertEqual (editor.GetSelectionEnd(), 8)


    def testSearchPrev (self):
        editor = self._getEditor()
        editor.SetText (u"Абырвалг проверка абырвалг")
        editor.SetSelection (0, 0)

        searchController = editor.searchPanel

        searchController.setSearchPhrase (u"абырвалг")

        searchController.prevSearch()
        self.assertEqual (editor.GetSelectionStart(), 18)
        self.assertEqual (editor.GetSelectionEnd(), 26)

        searchController.prevSearch()
        self.assertEqual (editor.GetSelectionStart(), 0)
        self.assertEqual (editor.GetSelectionEnd(), 8)

        searchController.prevSearch()
        self.assertEqual (editor.GetSelectionStart(), 18)
        self.assertEqual (editor.GetSelectionEnd(), 26)


    def testSearchSiblingsNext (self):
        editor = self._getEditor()
        editor.SetText (u"ыыыыыыыыы")
        editor.SetSelection (0, 0)

        searchController = editor.searchPanel

        searchController.setSearchPhrase (u"ыыы")
        self.assertEqual (editor.GetSelectionStart(), 0)
        self.assertEqual (editor.GetSelectionEnd(), 3)
        
        searchController.nextSearch()
        self.assertEqual (editor.GetSelectionStart(), 3)
        self.assertEqual (editor.GetSelectionEnd(), 6)
        
        searchController.nextSearch()
        self.assertEqual (editor.GetSelectionStart(), 6)
        self.assertEqual (editor.GetSelectionEnd(), 9)
        
        searchController.nextSearch()
        self.assertEqual (editor.GetSelectionStart(), 0)
        self.assertEqual (editor.GetSelectionEnd(), 3)


    def testSearchSiblingsPrev (self):
        editor = self._getEditor()
        editor.SetText (u"ыыыыыыыыы")
        editor.SetSelection (0, 0)

        searchController = editor.searchPanel

        searchController.setSearchPhrase (u"ыыы")
        searchController.prevSearch()
        self.assertEqual (editor.GetSelectionStart(), 6)
        self.assertEqual (editor.GetSelectionEnd(), 9)
        
        searchController.prevSearch()
        self.assertEqual (editor.GetSelectionStart(), 3)
        self.assertEqual (editor.GetSelectionEnd(), 6)
        
        searchController.prevSearch()
        self.assertEqual (editor.GetSelectionStart(), 0)
        self.assertEqual (editor.GetSelectionEnd(), 3)
