#!/usr/bin/python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta

import wx.stc

from outwiker.gui.texteditor import TextEditor
from .wikicolorizer import WikiColorizer, EVT_APPLY_STYLE

# Событие вызывается с помощью PostEvent для потокобезопасного применения стилей к редактору


class WikiEditor (TextEditor):
    def __init__ (self, parent):
        self.__createStyles()
        super (WikiEditor, self).__init__ (parent)

        self._colorizer = WikiColorizer (self)

        self.textCtrl.Bind (wx.stc.EVT_STC_STYLENEEDED, self.__onStyleNeeded)
        self.textCtrl.Bind (wx.stc.EVT_STC_CHANGE, self.__onChange)
        self.Bind (EVT_APPLY_STYLE, self.__onApplyStyle)

        # Уже были установлены стили текста (раскраска)
        self.__styleSet = False
        # Начинаем раскраску кода не менее чем через это время с момента его изменения
        self.__DELAY = timedelta (milliseconds=300)

        # Время последней модификации текста страницы. 
        # Используется для замера времени после модификации, чтобы не парсить текст
        # после каждой введенной буквы
        self.__lastEdit = datetime.now()


    def __createStyles (self):
        self._styles = {}

        # Константы для стилей
        self.STYLE_BOLD_ID = 1
        self.STYLE_ITALIC_ID = 2
        self.STYLE_UNDERLINE_ID = 4
        self.STYLE_LINK_ID = 8
        self.STYLE_HEADING_ID = 126
        self.STYLE_COMMAND_ID = 125

        # Комбинации стилей
        self.STYLE_BOLD_ITALIC_UNDERLINE_ID = (self.STYLE_BOLD_ID | 
                self.STYLE_ITALIC_ID | 
                self.STYLE_UNDERLINE_ID)

        self.STYLE_BOLD_ITALIC_ID = self.STYLE_BOLD_ID | self.STYLE_ITALIC_ID
        self.STYLE_BOLD_UNDERLINE_ID = self.STYLE_BOLD_ID | self.STYLE_UNDERLINE_ID
        self.STYLE_ITALIC_UNDERLINE_ID = self.STYLE_ITALIC_ID | self.STYLE_UNDERLINE_ID

        self.STYLE_LINK_BOLD_ITALIC_UNDERLINE_ID = (self.STYLE_BOLD_ID | 
                self.STYLE_ITALIC_ID |
                self.STYLE_UNDERLINE_ID |
                self.STYLE_LINK_ID )

        self.STYLE_LINK_ITALIC_UNDERLINE_ID = (self.STYLE_ITALIC_ID | 
                self.STYLE_UNDERLINE_ID |
                self.STYLE_LINK_ID )

        self.STYLE_LINK_BOLD_UNDERLINE_ID = (self.STYLE_BOLD_ID | 
                self.STYLE_UNDERLINE_ID |
                self.STYLE_LINK_ID )

        self.STYLE_LINK_BOLD_ITALIC_ID = (self.STYLE_BOLD_ID | 
                self.STYLE_ITALIC_ID |
                self.STYLE_LINK_ID )

        self.STYLE_LINK_ITALIC_ID = self.STYLE_ITALIC_ID | self.STYLE_LINK_ID 

        self.STYLE_LINK_UNDERLINE_ID = self.STYLE_UNDERLINE_ID | self.STYLE_LINK_ID 

        self.STYLE_LINK_BOLD_ID = self.STYLE_BOLD_ID | self.STYLE_LINK_ID


        # Заполняем словарь стилей
        self._styles[self.STYLE_BOLD_ID] = "bold"
        self._styles[self.STYLE_ITALIC_ID] = "italic"
        self._styles[self.STYLE_UNDERLINE_ID] = "underline"
        self._styles[self.STYLE_BOLD_ITALIC_UNDERLINE_ID] = "bold,italic,underline"
        self._styles[self.STYLE_BOLD_ITALIC_ID] = "bold,italic"
        self._styles[self.STYLE_BOLD_UNDERLINE_ID] = "bold,underline"
        self._styles[self.STYLE_ITALIC_UNDERLINE_ID] = "italic,underline"
        self._styles[self.STYLE_LINK_ID] = "fore:#0000FF,underline"
        self._styles[self.STYLE_LINK_BOLD_ITALIC_UNDERLINE_ID] = self._styles[self.STYLE_LINK_ID] + ",bold,italic,underline"
        self._styles[self.STYLE_LINK_ITALIC_UNDERLINE_ID] = self._styles[self.STYLE_LINK_ID] + ",italic,underline"
        self._styles[self.STYLE_LINK_BOLD_UNDERLINE_ID] = self._styles[self.STYLE_LINK_ID] + ",bold,underline"
        self._styles[self.STYLE_LINK_UNDERLINE_ID] = self._styles[self.STYLE_LINK_ID] + ",underline"
        self._styles[self.STYLE_LINK_BOLD_ITALIC_ID] = self._styles[self.STYLE_LINK_ID] + ",bold,italic"
        self._styles[self.STYLE_LINK_ITALIC_ID] = self._styles[self.STYLE_LINK_ID] + ",italic"
        self._styles[self.STYLE_LINK_BOLD_ID] = self._styles[self.STYLE_LINK_ID] + ",bold"
        self._styles[self.STYLE_HEADING_ID] = "bold"
        self._styles[self.STYLE_COMMAND_ID] = "fore:#6A686B"


    def setDefaultSettings (self):
        super (WikiEditor, self).setDefaultSettings()

        self.textCtrl.SetLexer (wx.stc.STC_LEX_CONTAINER)
        self.textCtrl.SetModEventMask(wx.stc.STC_MOD_INSERTTEXT | wx.stc.STC_MOD_DELETETEXT)
        self.textCtrl.SetStyleBits (7)

        for (styleid, style) in self._styles.items():
            self.__setStyleDefault (styleid)
            self.textCtrl.StyleSetSpec (styleid, style)

        self.__setStyleHeading()


    def __setStyleHeading (self):
        self.textCtrl.StyleSetSize (self.STYLE_HEADING_ID, self.config.fontSize.value + 2)
        self.textCtrl.StyleSetFaceName (self.STYLE_HEADING_ID, self.config.fontName.value)
        self.textCtrl.StyleSetSpec (self.STYLE_HEADING_ID, self._styles[self.STYLE_HEADING_ID])


    def __setStyleDefault (self, styleId):
        self.textCtrl.StyleSetSize (styleId, self.config.fontSize.value)
        self.textCtrl.StyleSetFaceName (styleId, self.config.fontName.value)


    def __onChange (self, event):
        self.__styleSet = False
        self.__lastEdit = datetime.now()


    def __getTextForParse (self):
        # Табуляция в редакторе считается за несколько символов
        return self.textCtrl.GetText().replace ("\t", " ")


    def __onStyleNeeded (self, event):
        if (self.__styleSet or
                datetime.now() - self.__lastEdit < self.__DELAY):
            return

        text = self.__getTextForParse()
        self._colorizer.start (text)


    def __onApplyStyle (self, event):
        if event.text == self.__getTextForParse():
            self.__applyStyles (event.stylebytes)
    

    def __applyStyles (self, stylebytes):
        self.textCtrl.StartStyling (0, 0xff)
        self.textCtrl.SetStyleBytes (len (stylebytes), stylebytes)
        self.__styleSet = True


    def turnList (self, itemStart):
        """
        Создать список
        """
        selText = self.textCtrl.GetSelectedText()
        items = filter (lambda item: len (item.strip()) > 0, selText.split ("\n") )

        # Собираем все элементы
        if len (items) > 0:
            itemsList = reduce (lambda result, item: result + itemStart + item.strip() + "\n", items, u"")
        else:
            itemsList = itemStart + "\n"

        itemsList = itemsList[: -1]

        self.textCtrl.ReplaceSelection (itemsList)
