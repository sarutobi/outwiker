# -*- coding: utf-8 -*-

import unittest

from outwiker.actions.polyactionsid import *
from outwiker.pages.html.htmlpage import HtmlPageFactory
from outwiker.tests.basetestcases import BaseOutWikerGUIMixin


class HtmlActionsTest(unittest.TestCase, BaseOutWikerGUIMixin):
    """
    Тесты действий для HTML-страницы
    """

    def setUp(self):
        self.initApplication()
        self.wikiroot = self.createWiki()

        self._turnSyntax = [
            (BOLD_STR_ID, "<b>", "</b>"),
            (ITALIC_STR_ID, "<i>", "</i>"),
            (BOLD_ITALIC_STR_ID, "<b><i>", "</i></b>"),
            (UNDERLINE_STR_ID, "<u>", "</u>"),
            (STRIKE_STR_ID, "<strike>", "</strike>"),
            (SUBSCRIPT_STR_ID, "<sub>", "</sub>"),
            (SUPERSCRIPT_STR_ID, "<sup>", "</sup>"),
            (ALIGN_LEFT_STR_ID, '<div align="left">', '</div>'),
            (ALIGN_CENTER_STR_ID, '<div align="center">', '</div>'),
            (ALIGN_RIGHT_STR_ID, '<div align="right">', '</div>'),
            (ALIGN_JUSTIFY_STR_ID, '<div align="justify">', '</div>'),
            (HEADING_1_STR_ID, "<h1>", "</h1>"),
            (HEADING_2_STR_ID, "<h2>", "</h2>"),
            (HEADING_3_STR_ID, "<h3>", "</h3>"),
            (HEADING_4_STR_ID, "<h4>", "</h4>"),
            (HEADING_5_STR_ID, "<h5>", "</h5>"),
            (HEADING_6_STR_ID, "<h6>", "</h6>"),
            (PREFORMAT_STR_ID, "<pre>", "</pre>"),
            (CODE_STR_ID, "<code>", "</code>"),
            (ANCHOR_STR_ID, '<a name="', '"></a>'),
            (QUOTE_STR_ID, '<blockquote>', '</blockquote>'),
            (IMAGE_STR_ID, '<img src="', '"/>'),
        ]

        self._replaceSyntax = [
            (HORLINE_STR_ID, "<hr>"),
        ]

        HtmlPageFactory().create(self.wikiroot, "HTML-страница", [])
        HtmlPageFactory().create(self.wikiroot, "temp", [])

        # Страница, куда будем переключаться перед изменением содержимого основной страницы
        # Можно было бы вместо temppage использовать None, но тогда программе
        # пришлось бы каждый раз удалять и создавать панели инструментов, что медленно
        self.temppage = self.wikiroot["temp"]
        self.testpage = self.wikiroot["HTML-страница"]

        self.application.wikiroot = self.wikiroot
        self.application.selectedPage = self.testpage

    def tearDown(self):
        self.destroyApplication()
        self.destroyWiki(self.wikiroot)

    def _getEditor(self):
        return self.application.mainWindow.pagePanel.pageView.codeEditor

    def testTurnSyntaxEmpty(self):
        for syntax in self._turnSyntax:
            self.application.selectedPage = self.temppage
            self.testpage.content = ""
            self.application.selectedPage = self.testpage

            self.application.actionController.getAction(syntax[0]).run(None)
            self.assertEqual(self._getEditor().GetText(),
                             syntax[1] + syntax[2])

    def testTurnSyntaxSelectedAll(self):
        text = "Бла-бла-бла"

        for syntax in self._turnSyntax:
            self.application.selectedPage = self.temppage
            self.testpage.content = text
            self.application.selectedPage = self.testpage

            self._getEditor().SetSelection(0, len(text))

            self.application.actionController.getAction(syntax[0]).run(None)
            self.assertEqual(self._getEditor().GetText(),
                             syntax[1] + "Бла-бла-бла" + syntax[2])

    def testTurnSyntaxSelectedPart(self):
        text = "Бла-бла-бла"

        for syntax in self._turnSyntax:
            self.application.selectedPage = self.temppage
            self.testpage.content = text
            self.application.selectedPage = self.testpage

            self._getEditor().SetSelection(4, 7)

            self.application.actionController.getAction(syntax[0]).run(None)
            self.assertEqual(self._getEditor().GetText(),
                             "Бла-{}бла{}-бла".format(syntax[1], syntax[2]))

    def testReplaceSyntaxEmpty(self):
        for syntax in self._replaceSyntax:
            self.application.selectedPage = self.temppage
            self.testpage.content = ""
            self.application.selectedPage = self.testpage

            self.application.actionController.getAction(syntax[0]).run(None)
            self.assertEqual(self._getEditor().GetText(), syntax[1])

    def testReplaceSyntaxSelectedAll(self):
        text = "Бла-бла-бла"

        for syntax in self._replaceSyntax:
            self.application.selectedPage = self.temppage
            self.testpage.content = text
            self.application.selectedPage = self.testpage

            self._getEditor().SetSelection(0, len(text))

            self.application.actionController.getAction(syntax[0]).run(None)
            self.assertEqual(self._getEditor().GetText(), syntax[1])

    def testReplaceSyntaxSelectedPart(self):
        text = "Бла-бла-бла"

        for syntax in self._replaceSyntax:
            self.application.selectedPage = self.temppage
            self.testpage.content = text
            self.application.selectedPage = self.testpage

            self._getEditor().SetSelection(4, 7)

            self.application.actionController.getAction(syntax[0]).run(None)
            self.assertEqual(self._getEditor().GetText(),
                             "Бла-{}-бла".format(syntax[1]))

    def testListBulletsEmpty(self):
        result = """<ul>
<li></li>
</ul>"""

        self.application.selectedPage = self.temppage
        self.testpage.content = ""
        self.application.selectedPage = self.testpage

        self.application.actionController.getAction(
            LIST_BULLETS_STR_ID).run(None)
        self.assertEqual(self._getEditor().GetText(), result)

    def testListNumbersEmpty(self):
        result = """<ol>
<li></li>
</ol>"""

        self.application.selectedPage = self.temppage
        self.testpage.content = ""
        self.application.selectedPage = self.testpage

        self.application.actionController.getAction(LIST_NUMBERS_STR_ID).run(None)
        self.assertEqual(self._getEditor().GetText(), result)

    def testListBulletsSelectedAll(self):
        text = """йцкуйцук
укеуке
ывапвыап
ывапвыапыап
ывапываппа"""

        result = """<ul>
<li>йцкуйцук</li>
<li>укеуке</li>
<li>ывапвыап</li>
<li>ывапвыапыап</li>
<li>ывапываппа</li>
</ul>"""

        self.application.selectedPage = self.temppage
        self.testpage.content = text
        self.application.selectedPage = self.testpage

        self._getEditor().SetSelection(0, len (text))

        self.application.actionController.getAction(LIST_BULLETS_STR_ID).run(None)
        self.assertEqual(self._getEditor().GetText(), result)

    def testListNumbersSelectedAll(self):
        text = """йцкуйцук
укеуке
ывапвыап
ывапвыапыап
ывапываппа"""

        result = """<ol>
<li>йцкуйцук</li>
<li>укеуке</li>
<li>ывапвыап</li>
<li>ывапвыапыап</li>
<li>ывапываппа</li>
</ol>"""

        self.application.selectedPage = self.temppage
        self.testpage.content = text
        self.application.selectedPage = self.testpage

        self._getEditor().SetSelection(0, len(text))

        self.application.actionController.getAction(LIST_NUMBERS_STR_ID).run(None)
        self.assertEqual(self._getEditor().GetText(), result)
