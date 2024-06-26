# -*- coding: utf-8 -*-

from outwiker.api.app.config import GeneralGuiConfig

from .i18n import get_


class DatePageInfo:
    """Класс для генерации информации о старых страницах и страницах,
    которые изменяли в последнее время"""

    def __init__(self, pageDateList, itemsCount, config):
        """
        itemsCount - количество выводимых страниц в списках
        """
        self._itemsCount = itemsCount
        self._pageDateList = pageDateList
        self._dateTimeFormat = GeneralGuiConfig(config).dateTimeFormat.value

        global _
        _ = get_()

    @property
    def content(self):
        recentPages = self._getRecentEditedPages()
        oldPages = self._getOldestPages()

        return """{recentPages}
{oldPages}
<hr/>""".format(
            recentPages=recentPages, oldPages=oldPages
        )

    def _getRecentEditedPages(self):
        title = _("Recent edited pages:")
        pageList = self._pageDateList[
            0 : min(self._itemsCount, len(self._pageDateList))
        ]

        itemsHtml = self._getPageListHtml(pageList)
        return """<p>{title}<br>{items}</p>""".format(title=title, items=itemsHtml)

    def _getOldestPages(self):
        title = _("Oldest pages:")
        pageListRevert = self._pageDateList[:]
        pageListRevert.reverse()

        pageList = pageListRevert[0 : min(self._itemsCount, len(self._pageDateList))]

        itemsHtml = self._getPageListHtml(pageList)
        return """<p>{title}<br>{items}</p>""".format(title=title, items=itemsHtml)

    def _getPageListHtml(self, pageList):
        """
        Оформить список страниц в виде HTML
        """
        items = [
            "<li><b>{title}</b> ({date})</li>".format(
                title=page.display_subpath,
                date=page.datetime.strftime(self._dateTimeFormat),
            )
            if page.datetime is not None
            else ""
            for page in pageList
        ]

        return "<ul>" + "".join(items) + "</ul>"
