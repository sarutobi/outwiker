# -*- coding: utf-8 -*-

import re
from typing import List, Tuple

from pyparsing import Regex, OneOrMore, Combine

from outwiker.pages.wiki.parser.utils import noConvert
from outwiker.pages.wiki.parser.tokenmultilineblock import MultilineBlockFactory
import outwiker.core.cssclasses as css


class ListFactory:
    @staticmethod
    def make(parser):
        return ListToken(parser).getToken()


class ListParams:
    """
    Параметры списков в парсере
    """

    def __init__(self, symbol, startTag, endTag):
        self.symbol = symbol
        self.startTag = startTag
        self.endTag = endTag


class ListToken:
    """
    Класс для разбора списков
    """
    unorderList = "*"
    orderList = "#"

    unorderListCSS = [
            ('[]', css.CSS_LIST_ITEM_EMPTY),
            ('[ ]', css.CSS_LIST_ITEM_TODO),
            ('[/]', css.CSS_LIST_ITEM_INCOMPLETE),
            ('[\\]', css.CSS_LIST_ITEM_INCOMPLETE),
            ('[x]', css.CSS_LIST_ITEM_COMPLETE),
            ('[X]', css.CSS_LIST_ITEM_COMPLETE),
            ('[*]', css.CSS_LIST_ITEM_STAR),
            ('[+]', css.CSS_LIST_ITEM_PLUS),
            ('[-]', css.CSS_LIST_ITEM_MINUS),
            ('[o]', css.CSS_LIST_ITEM_CIRCLE),
            ('[O]', css.CSS_LIST_ITEM_CIRCLE),
            ('[v]', css.CSS_LIST_ITEM_CHECK),
            ('[V]', css.CSS_LIST_ITEM_CHECK),
            ('[<]', css.CSS_LIST_ITEM_LT),
            ('[>]', css.CSS_LIST_ITEM_GT),
            ]

    def __init__(self, parser):
        self.allListsParams = [
            ListParams(ListToken.unorderList, f'<ul class="{css.CSS_WIKI}">', '</ul>'),
            ListParams(ListToken.orderList, f'<ol class="{css.CSS_WIKI}">', '</ol>'),
        ]

        self.parser = parser
        self._maxDepthLevel = 500
        self._blockToken = MultilineBlockFactory.make(
            self.parser).setParseAction(noConvert)

    def _addDeeperLevel(self, depth, item, currItem):
        """
        Создать список более глубокого уровня
        depth - разница между новым уровнем и текущим
        item - разобранный элемент строки
        currItem - список вложенных списков
            (их первых символов для определения типа)
        """
        result = self._getStartListTag(item[0], self.allListsParams) * depth
        for _ in range(depth):
            currItem.append(item[0])

        return result

    def _closeLists(self, depth, currItem):
        """
        Закрыть один или несколько уровней списков (перейти выше)
        depth - разность между текущим уровнем и новым урвонем
        """
        result = self._getEndListTag(currItem[-1], self.allListsParams) * depth
        for _ in range(depth):
            del currItem[-1]

        return result

    def _closeListStartList(self, level, item, currItem):
        result = ''

        result += self._closeLists(1, currItem)
        result += self._getStartListTag(item[0], self.allListsParams)
        currItem.append(item[0])

        result += self._getListItemTag(item, level)

        return result

    def _generateListForItems(self, items):
        currLevel = 0
        currItem = []

        result = ''

        for item in items:
            if len(item.strip()) == 0:
                continue

            level = self._getListLevel(item, self.allListsParams)
            if level > self._maxDepthLevel:
                level = self._maxDepthLevel

            if (level == currLevel and
                    len(currItem) > 0 and
                    item[0] == currItem[-1]):
                # Новый элемент в текущем списке
                result += self._getListItemTag(item, level)

            elif level > currLevel:
                # Более глубокий уровень
                result += self._addDeeperLevel(level -
                                                currLevel, item, currItem)
                result += self._getListItemTag(item, level)

            elif level < currLevel:
                # Более высокий уровень, но тот же тип списка
                result += self._closeLists(currLevel - level, currItem)

                if item[0] == currItem[-1]:
                    result += self._getListItemTag(item, level)
                else:
                    result += self._closeListStartList(level, item, currItem)

            elif level == currLevel and len(currItem) > 0 and item[0] != currItem[-1]:
                # Тот же уровень, но другой список
                result += self._closeListStartList(level, item, currItem)

            else:
                assert False

            currLevel = level

        result += self._closeLists(currLevel, currItem)

        return result

    def getToken(self):
        text = Regex(r"(?:\\\n|.)*?$", re.MULTILINE)
        line_break = Regex(r'\n{0,2}', re.MULTILINE)

        item = Combine(Regex(r'^(?:(?:\*+)|(?:#+))\s*', re.MULTILINE) +
                       (self._blockToken | text) +
                       line_break).leaveWhitespace()
        fullList = OneOrMore(item).setParseAction(self._convertList).ignoreWhitespace(False)("list")

        return fullList

    def _convertList(self, s, loc, tokens):
        """
        Преобразовать список элементов списка в HTML-список
        (возможно, вложенный)
        """
        return self._generateListForItems(tokens)

    def _getListLevel(self, item, params):
        """
        Получить уровень списка по его элементу
        (количество символов # и * в начале строки)
        """
        found = False
        for param in params:
            if item[0] == param.symbol:
                found = True
                break

        if not found:
            return 0

        level = 1
        while level < len(item) and item[level] == item[0]:
            level += 1

        return level

    def _getListItemTag(self, item: str, level: int) -> str:
        text = (item[level:]).strip()
        css_classes = [css.CSS_WIKI]

        if item[level - 1] == self.unorderList:
            # Find classes for unorder lists
            text, other_css = self._processUnorderClasses(text)
            css_classes += other_css

        itemText = self.parser.parseListItemMarkup(text)
        return '<li class="{css_class}">{text}</li>'.format(text=itemText, css_class=' '.join(css_classes))

    def _processUnorderClasses(self, text) -> Tuple[str, List[str]]:
        result_text = text
        classes: List[str] = []

        for prefix, css_class in self.unorderListCSS:
            if text.startswith(prefix):
                result_text = text[len(prefix):].strip()
                classes.append(css_class)
                break

        return (result_text, classes)

    def _getStartListTag(self, symbol, params):
        """
        Получить открывающийся тег для элемента
        """
        for listparam in params:
            if listparam.symbol == symbol:
                return listparam.startTag

    def _getEndListTag(self, symbol, params):
        """
        Получить закрывающийся тег для элемента
        """
        for listparam in params:
            if listparam.symbol == symbol:
                return listparam.endTag
