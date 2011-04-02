#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import unittest
import hashlib

from utils import removeWiki

from core.tree import WikiDocument
from core.attachment import Attachment
from core.application import Application

from pages.wiki.parser.wikiparser import Parser
from pages.wiki.wikipage import WikiPageFactory
from pages.wiki.thumbnails import Thumbnails
from pages.wiki.texrender import getTexRender
from pages.wiki.parser.commandtest import TestCommand, ExceptionCommand
from pages.wiki.parserfactory import ParserFactory


class ParserTest (unittest.TestCase):
	def setUp(self):
		self.encoding = "utf8"

		self.filesPath = u"../test/samplefiles/"

		self.url1 = u"http://example.com"
		self.url2 = u"http://jenyay.net/Photo/Nature?action=imgtpl&G=1&upname=tsaritsyno_01.jpg"

		self.pagelinks = [u"Страница 1", u"/Страница 1", u"/Страница 2/Страница 3"]
		self.pageComments = [u"Страницо 1", u"Страницо 1", u"Страницо 3"]

		self.__createWiki()
		
		factory = ParserFactory()
		self.parser = factory.make (self.testPage, Application.config)
	

	def __createWiki (self):
		# Здесь будет создаваться вики
		self.path = u"../test/testwiki"
		removeWiki (self.path)

		self.rootwiki = WikiDocument.create (self.path)
		WikiPageFactory.create (self.rootwiki, u"Страница 2", [])
		self.testPage = self.rootwiki[u"Страница 2"]
		
		files = [u"accept.png", u"add.png", u"anchor.png", u"filename.tmp", 
				u"файл с пробелами.tmp", u"картинка с пробелами.png", 
				u"image.jpg", u"image.jpeg", u"image.png", u"image.tif", u"image.tiff", u"image.gif",
				u"image_01.JPG", u"dir", u"dir.xxx", u"dir.png"]

		fullFilesPath = [os.path.join (self.filesPath, fname) for fname in files]

		self.attach_page2 = Attachment (self.rootwiki[u"Страница 2"])

		# Прикрепим к двум страницам файлы
		Attachment (self.testPage).attach (fullFilesPath)
	

	def tearDown(self):
		removeWiki (self.path)
	

	def testParseWithoutAttaches (self):
		pagetitle = u"Страница 666"
		
		WikiPageFactory.create (self.rootwiki, pagetitle, [])
		parser = Parser(self.rootwiki[pagetitle], Application.config)

		parser.toHtml (u"Attach:bla-bla-bla")


	def testBold (self):
		text = u"'''Полужирный'''"
		result = u"<B>Полужирный</B>"

		self.assertEqual (self.parser.toHtml (text), result)


	def testItalic (self):
		text = u"''Курсив''"
		result = u"<I>Курсив</I>"

		self.assertEqual (self.parser.toHtml (text), result)

	
	def testBoldItalic (self):
		text = u"''''Полужирный курсив''''"
		result = u"<B><I>Полужирный курсив</I></B>"

		self.assertEqual (self.parser.toHtml (text), result)
	

	def testComboBoldItalic (self):
		text = u"Обычный текст \n''курсив'' \n'''полужирный ''внутри \nкурсив'' ''' 111"
		result = u"Обычный текст \n<I>курсив</I> \n<B>полужирный <I>внутри \nкурсив</I> </B> 111"

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testMonospaced (self):
		text = u"бла-бла-бла @@моноширинный текст@@ бла-бла-бла"
		result = u"бла-бла-бла <CODE>моноширинный текст</CODE> бла-бла-бла"

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testPreformat1 (self):
		text = u"[@ '''Полужирный''' \n''Курсив'' @]"
		result = u"<PRE> '''Полужирный''' \n''Курсив'' </PRE>"

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testPreformat2 (self):
		text = u'бла-бла-бла [@ <a href="http://jenyay.net/&param">jenyay.net</a> @] foo bar'
		result = u"бла-бла-бла <PRE> &lt;a href=&quot;http://jenyay.net/&amp;param&quot;&gt;jenyay.net&lt;/a&gt; </PRE> foo bar"

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testNoformat (self):
		text = u"[= '''Полужирный''' \n''Курсив'' =]"
		result = u" '''Полужирный''' \n''Курсив'' "

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUrl1 (self):
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (self.url1)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url1, self.url1)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUrl2 (self):
		text = u"бла-бла-бла \ntest %s бла-бла-бла\nбла-бла-бла" % (self.url2)
		result = u'бла-бла-бла \ntest <A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url2, self.url2)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testLink1 (self):
		text = u"бла-бла-бла \n[[%s]] бла-бла-бла\nбла-бла-бла" % (self.url1)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url1, self.url1)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testLink2 (self):
		text = u"бла-бла-бла \n[[%s]] бла-бла-бла\nбла-бла-бла" % (self.url2)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url2, self.url2)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testLink3 (self):
		url = "http://jenyay.net/social/feed.png"

		text = u"бла-бла-бла \n[[%s]] бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (url, url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testCommentLink1 (self):
		comment = u"Ссылко"
		text = u"бла-бла-бла \n[[%s | %s]] бла-бла-бла\nбла-бла-бла" % (self.url2, comment)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url2, comment)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testCommentLink2 (self):
		comment = u"Ссылко"
		text = u"бла-бла-бла \n[[%s -> %s]] бла-бла-бла\nбла-бла-бла" % (comment, self.url2)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url2, comment)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testCommentLink3 (self):
		comment = u"Ссылко с '''полужирным''' текстом"
		text = u"бла-бла-бла \n[[%s | %s]] бла-бла-бла\nбла-бла-бла" % (self.url2, comment)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url2, u"Ссылко с <B>полужирным</B> текстом")

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testCommentLink4 (self):
		comment = u"Ссылко с '''полужирным''' текстом"
		text = u"бла-бла-бла \n[[%s -> %s]] бла-бла-бла\nбла-бла-бла" % (comment, self.url2)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url2, u"Ссылко с <B>полужирным</B> текстом")

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testCommentLink5 (self):
		text = u"бла-бла-бла \n[[%s -> %s]] бла-бла-бла\nбла-бла-бла" % (self.url1, self.url1)
		result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (self.url1, self.url1)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testPageLinks (self):
		for link in self.pagelinks:
			text = u"бла-бла-бла \n[[%s]] бла-бла-бла\nбла-бла-бла" % (link)
			result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (link, link)

			self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testPageCommentsLinks1 (self):
		for n in range ( len (self.pagelinks)):
			link = self.pagelinks[n]
			comment = self.pageComments[n]

			text = u"бла-бла-бла \n[[%s | %s]] бла-бла-бла\nбла-бла-бла" % (link, comment)
			result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (link, comment)

			self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testPageCommentsLinks2 (self):
		for n in range ( len (self.pagelinks)):
			link = self.pagelinks[n]
			comment = self.pageComments[n]

			text = u"бла-бла-бла \n[[%s -> %s]] бла-бла-бла\nбла-бла-бла" % (comment, link)
			result = u'бла-бла-бла \n<A HREF="%s">%s</A> бла-бла-бла\nбла-бла-бла' % (link, comment)

			self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testAttach01 (self):
		fname = u"filename.tmp"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">%s</A> бла-бла-бла\nбла-бла-бла' % (fname, fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testAttach02 (self):
		fname = u"accept.png"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<IMG SRC="__attach/%s"> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testAttach03 (self):
		fname = u"filename.tmp"
		text = u"бла-бла-бла \n[[Attach:%s]] бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">%s</A> бла-бла-бла\nбла-бла-бла' % (fname, fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testAttach04 (self):
		fname = u"файл с пробелами.tmp"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">%s</A> бла-бла-бла\nбла-бла-бла' % (fname, fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testAttach05 (self):
		fname = u"файл с пробелами.tmp"
		text = u"бла-бла-бла \n[[Attach:%s]] бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">%s</A> бла-бла-бла\nбла-бла-бла' % (fname, fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testAttach06 (self):
		fname = u"картинка с пробелами.png"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<IMG SRC="__attach/%s"> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testAttach07 (self):
		fname = u"accept.png"
		text = u"бла-бла-бла \n[[Attach:%s]] бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">%s</A> бла-бла-бла\nбла-бла-бла' % (fname, fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testAttach08 (self):
		fname = u"accept.png"
		text = u"бла-бла-бла \n[[Attach:%s | Комментарий]] бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">Комментарий</A> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testAttach09 (self):
		fname = u"файл с пробелами.tmp"
		text = u"бла-бла-бла \n[[Attach:%s | Комментарий]] бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">Комментарий</A> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testAttach10 (self):
		fname = u"accept.png"
		text = u"бла-бла-бла \n[[Комментарий -> Attach:%s]] бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">Комментарий</A> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testAttach11 (self):
		fname = u"файл с пробелами.tmp"
		text = u"бла-бла-бла \n[[Комментарий -> Attach:%s]] бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">Комментарий</A> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	
	def testAttach12 (self):
		fname = u"image_01.JPG"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<IMG SRC="__attach/%s"> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testAttach13 (self):
		fname = u"dir.xxx"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">%s</A> бла-бла-бла\nбла-бла-бла' % (fname, fname)

		self.assertEqual (self.parser.toHtml (text), 
				result, 
				self.parser.toHtml (text).encode (self.encoding) + "\n" + result.encode (self.encoding))
	

	def testAttach14 (self):
		fname = u"dir"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<A HREF="__attach/%s">%s</A> бла-бла-бла\nбла-бла-бла' % (fname, fname)

		self.assertEqual (self.parser.toHtml (text), 
				result, 
				self.parser.toHtml (text).encode (self.encoding) + "\n" + result.encode (self.encoding))
	

	def testAttach15 (self):
		fname = u"dir.png"
		text = u"бла-бла-бла \nAttach:%s бла-бла-бла\nбла-бла-бла" % (fname)
		result = u'бла-бла-бла \n<IMG SRC="__attach/%s"> бла-бла-бла\nбла-бла-бла' % (fname)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testImage1 (self):
		url = u"http://jenyay.net/social/feed.png"
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testImage2 (self):
		url = u"http://jenyay.net/social/feed.jpg"
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testImage3 (self):
		url = u"http://jenyay.net/social/feed.jpeg"
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testImage4 (self):
		url = u"http://jenyay.net/social/feed.bmp"
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testImage5 (self):
		url = u"http://jenyay.net/social/feed.tif"
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testImage6 (self):
		url = u"http://jenyay.net/social/feed.tiff"
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testImage7 (self):
		url = u"http://jenyay.net/social/feed.gif"
		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testImage8 (self):
		url = u"http://www.wuala.com/jenyayIlin/Photos/%D0%A1%D0%BC%D0%BE%D0%BB%D0%B5%D0%BD%D1%81%D0%BA.%20%D0%96%D0%B8%D0%B2%D0%BE%D1%82%D0%BD%D1%8B%D0%B5/smolensk_animals_01.jpg"

		text = u"бла-бла-бла \n%s бла-бла-бла\nбла-бла-бла" % (url)
		result = u'бла-бла-бла \n<IMG SRC="%s"> бла-бла-бла\nбла-бла-бла' % (url)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testHeader1 (self):
		text = u"бла-бла-бла \n!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<H1>Заголовок бла-бла-бла</H1>\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testHeader2 (self):
		text = u"бла-бла-бла \n!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<H2>Заголовок бла-бла-бла</H2>\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testHeader3 (self):
		text = u"бла-бла-бла \n!!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<H3>Заголовок бла-бла-бла</H3>\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testHeader4 (self):
		text = u"бла-бла-бла \n!!!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<H4>Заголовок бла-бла-бла</H4>\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testHeader5 (self):
		text = u"бла-бла-бла \n!!!!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<H5>Заголовок бла-бла-бла</H5>\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testHeader6 (self):
		text = u"бла-бла-бла \n!!!!!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<H6>Заголовок бла-бла-бла</H6>\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testHeader7 (self):
		text = u"бла-бла-бла \nкхм !! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм !! Заголовок бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testHeader8 (self):
		text = u"бла-бла-бла \nкхм !!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм !!! Заголовок бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testHeader9 (self):
		text = u"бла-бла-бла \nкхм !!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм !!!! Заголовок бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testHeader10 (self):
		text = u"бла-бла-бла \nкхм !!!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм !!!!! Заголовок бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testHeader11 (self):
		text = u"бла-бла-бла \nкхм !!!!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм !!!!!! Заголовок бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testHeader11 (self):
		text = u"бла-бла-бла \nкхм !!!!!!! Заголовок бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм !!!!!!! Заголовок бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testThumbWidthJpg (self):
		text = u'бла-бла-бла \nкхм % width = 100 px % Attach:image.jpg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_width_100_image.jpg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_width_100_image.jpg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testThumbWidthJpg2 (self):
		text = u'бла-бла-бла \nкхм % thumb width = 100 px % Attach:image.jpg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_width_100_image.jpg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_width_100_image.jpg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testThumbWidthJpeg (self):
		text = u'бла-бла-бла \nкхм % width = 100 px % Attach:image.jpeg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_width_100_image.jpeg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpeg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_width_100_image.jpeg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))

	
	def testThumbWidthGif (self):
		text = u'бла-бла-бла \nкхм % width = 100 px % Attach:image.gif %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_width_100_image.png")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.gif"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_width_100_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testThumbWidthPng (self):
		text = u'бла-бла-бла \nкхм % width = 100 px % Attach:image.png %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_width_100_image.png")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.png"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_width_100_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testThumbHeightJpg (self):
		text = u'бла-бла-бла \nкхм % height = 100 px % Attach:image.jpg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_height_100_image.jpg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_height_100_image.jpg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))

	
	def testThumbHeightJpg2 (self):
		text = u'бла-бла-бла \nкхм % thumb height = 100 px % Attach:image.jpg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_height_100_image.jpg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format(path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_height_100_image.jpg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))


	def testThumbHeightJpeg (self):
		text = u'бла-бла-бла \nкхм % height = 100 px % Attach:image.jpeg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_height_100_image.jpeg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpeg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_height_100_image.jpeg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))

	
	def testThumbHeightGif (self):
		text = u'бла-бла-бла \nкхм % height = 100 px % Attach:image.gif %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_height_100_image.png")
		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.gif"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_height_100_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testThumbHeightPng (self):
		text = u'бла-бла-бла \nкхм % height = 100 px % Attach:image.png %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_height_100_image.png")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.png"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_height_100_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testThumbJpg (self):
		text = u'бла-бла-бла \nкхм % thumb % Attach:image.jpg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_250_image.jpg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_250_image.jpg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))

	
	def testThumbJpeg (self):
		text = u'бла-бла-бла \nкхм % thumb % Attach:image.jpeg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_250_image.jpeg")
		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpeg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_250_image.jpeg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))


	def testThumbPng (self):
		text = u'бла-бла-бла \nкхм % thumb % Attach:image.png %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_250_image.png")
		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.png"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_250_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))

	
	def testThumbGif (self):
		text = u'бла-бла-бла \nкхм % thumb % Attach:image.gif %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_250_image.png")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.gif"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path = path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_250_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testThumbMaxSizeJpg (self):
		text = u'бла-бла-бла \nкхм % maxsize = 300 % Attach:image.jpg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_300_image.jpg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_300_image.jpg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))


	def testThumbMaxSizeJpg2 (self):
		text = u'бла-бла-бла \nкхм % maxsize = 300 % Attach:image.jpg %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_300_image.jpg")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.jpg"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_300_image.jpg")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))

	
	def testThumbMaxSizePng (self):
		text = u'бла-бла-бла \nкхм % maxsize = 300 % Attach:image.png %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_300_image.png")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.png"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_300_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))


	def testThumbMaxSizeGif (self):
		text = u'бла-бла-бла \nкхм % maxsize = 300 % Attach:image.gif %% бла-бла-бла\nбла-бла-бла'
		path = os.path.join ("__attach", "__thumb", "th_maxsize_300_image.png")

		result = u'бла-бла-бла \nкхм <A HREF="__attach/image.gif"><IMG SRC="{path}"></A> бла-бла-бла\nбла-бла-бла'.format (path=path)

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

		path = os.path.join (self.attach_page2.getAttachPath(), "__thumb/th_maxsize_300_image.png")
		self.assertTrue (os.path.exists (path), path.encode (self.encoding))
	

	def testUnderline (self):
		text = u'бла-бла-бла \nкхм {+ это подчеркивание+} %% бла-бла-бла\nбла-бла-бла'
		result = u'бла-бла-бла \nкхм <U> это подчеркивание</U> %% бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testSuperscript (self):
		text = u"бла-бла-бла \nкхм '^ это верхний индекс^' бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм <SUP> это верхний индекс</SUP> бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testSubscript (self):
		text = u"бла-бла-бла \nкхм '_ это нижний индекс_' бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм <SUB> это нижний индекс</SUB> бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testHorLine (self):
		text = u"бла-бла-бла \nкхм ---- бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \nкхм <HR> бла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testCenter1 (self):
		text = u"бла-бла-бла \n%center%кхм бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<DIV ALIGN="CENTER">кхм бла-бла-бла\nбла-бла-бла</DIV>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testCenter2 (self):
		text = u"бла-бла-бла \n%center%кхм бла-бла-бла\n\nбла-бла-бла"
		result = u'бла-бла-бла \n<DIV ALIGN="CENTER">кхм бла-бла-бла</DIV>\n\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testCenter3 (self):
		text = u"%center%бла-бла-бла \nкхм бла-бла-бла\n\nбла-бла-бла"
		result = u'<DIV ALIGN="CENTER">бла-бла-бла \nкхм бла-бла-бла</DIV>\n\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testCenter4 (self):
		text = u"%center%бла-бла-бла \n'''кхм''' бла-бла-бла\n\nбла-бла-бла"
		result = u'<DIV ALIGN="CENTER">бла-бла-бла \n<B>кхм</B> бла-бла-бла</DIV>\n\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testCenter5 (self):
		text = u"бла-бла-бла \n\n% center %Attach:accept.png\n\nбла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n\n<DIV ALIGN="CENTER"><IMG SRC="__attach/accept.png"></DIV>\n\nбла-бла-бла\nбла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testRight1 (self):
		text = u"бла-бла-бла \n% right %кхм бла-бла-бла\nбла-бла-бла"
		result = u'бла-бла-бла \n<DIV ALIGN="RIGHT">кхм бла-бла-бла\nбла-бла-бла</DIV>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testUnorderList1 (self):
		text = u"бла-бла-бла \n\n*Строка 1\n* Строка 2\n* Строка 3\nбла-бла-бла"
		result = u'бла-бла-бла \n\n<UL><LI>Строка 1</LI><LI>Строка 2</LI><LI>Строка 3</LI></UL>бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUnorderList2 (self):
		text = u"бла-бла-бла \n\n*'''Строка 1'''\n* ''Строка 2''\n* Строка 3\nбла-бла-бла"
		result = u'бла-бла-бла \n\n<UL><LI><B>Строка 1</B></LI><LI><I>Строка 2</I></LI><LI>Строка 3</LI></UL>бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testOrderList1 (self):
		text = u"бла-бла-бла \n\n#Строка 1\n# Строка 2\n# Строка 3\nбла-бла-бла"
		result = u'бла-бла-бла \n\n<OL><LI>Строка 1</LI><LI>Строка 2</LI><LI>Строка 3</LI></OL>бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testOrderList2 (self):
		text = u"бла-бла-бла \n\n#'''Строка 1'''\n# ''Строка 2''\n# Строка 3\nбла-бла-бла"
		result = u'бла-бла-бла \n\n<OL><LI><B>Строка 1</B></LI><LI><I>Строка 2</I></LI><LI>Строка 3</LI></OL>бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testEnclosureUnorderList1 (self):
		text = u"бла-бла-бла \n\n*Строка 1\n* Строка 2\n** Вложенная строка 1\n**Вложенная строка 2\n* Строка 3\nбла-бла-бла"
		result = u'бла-бла-бла \n\n<UL><LI>Строка 1</LI><LI>Строка 2</LI><UL><LI>Вложенная строка 1</LI><LI>Вложенная строка 2</LI></UL><LI>Строка 3</LI></UL>бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testEnclosureOrderList1 (self):
		text = u"бла-бла-бла \n\n#Строка 1\n# Строка 2\n## Вложенная строка 1\n##Вложенная строка 2\n# Строка 3\nбла-бла-бла"
		result = u'бла-бла-бла \n\n<OL><LI>Строка 1</LI><LI>Строка 2</LI><OL><LI>Вложенная строка 1</LI><LI>Вложенная строка 2</LI></OL><LI>Строка 3</LI></OL>бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testEnclosureList1 (self):
		text = u"""* Несортированный список. Элемент 1
* Несортированный список. Элемент 2
* Несортированный список. Элемент 3
## Вложенный сортированный список. Элемент 1
## Вложенный сортированный список. Элемент 2
## Вложенный сортированный список. Элемент 3
## Вложенный сортированный список. Элемент 4
*** Совсем вложенный сортированный список. Элемент 1
*** Совсем вложенный сортированный список. Элемент 2
## Вложенный сортированный список. Элемент 5
** Вложенный несортированный список. Элемент 1"""

		result = u'<UL><LI>Несортированный список. Элемент 1</LI><LI>Несортированный список. Элемент 2</LI><LI>Несортированный список. Элемент 3</LI><OL><LI>Вложенный сортированный список. Элемент 1</LI><LI>Вложенный сортированный список. Элемент 2</LI><LI>Вложенный сортированный список. Элемент 3</LI><LI>Вложенный сортированный список. Элемент 4</LI><UL><LI>Совсем вложенный сортированный список. Элемент 1</LI><LI>Совсем вложенный сортированный список. Элемент 2</LI></UL><LI>Вложенный сортированный список. Элемент 5</LI></OL><UL><LI>Вложенный несортированный список. Элемент 1</LI></UL></UL>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testEnclosureList2 (self):
		text = u"""* Строка 1
* Строка 2
** Строка 3
# Строка 4
# Строка 5
# Строка 6
# Строка 7"""

		result = u'<UL><LI>Строка 1</LI><LI>Строка 2</LI><UL><LI>Строка 3</LI></UL></UL><OL><LI>Строка 4</LI><LI>Строка 5</LI><LI>Строка 6</LI><LI>Строка 7</LI></OL>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testTable1 (self):
		text = u"""бла-бла-бла
|| border=1
|| Ячейка 1 ||Ячейка 2 || Ячейка 3||
||Ячейка 4||Ячейка 5||Ячейка 6||
"""
		
		result = u'''бла-бла-бла
<TABLE border=1><TR><TD ALIGN="CENTER">Ячейка 1</TD><TD ALIGN="LEFT">Ячейка 2</TD><TD ALIGN="RIGHT">Ячейка 3</TD></TR><TR><TD>Ячейка 4</TD><TD>Ячейка 5</TD><TD>Ячейка 6</TD></TR></TABLE>'''
	
		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testTable2 (self):
		text = u"""|| border=1
|| '''Синтаксис''' || '''Результат''' || '''Комментарий''' ||
||[@http://example.com@]||http://example.com||Ссылка на адрес в интернете||
||[@[[http://example.com]]@]||[[http://example.com]]||Ссылка на адрес в интернете||
||[@[[Пример ссылки -> http://example.com]]@]||[[Пример ссылки -> http://example.com]]||Ссылка на адрес в интернете с заданным текстом||
||[@[[http://example.com | Пример ссылки]]@]||[[http://example.com | Пример ссылки]]||Ссылка на адрес в интернете с заданным текстом||
"""
		
		result = u'''<TABLE border=1><TR><TD ALIGN="CENTER"><B>Синтаксис</B></TD><TD ALIGN="CENTER"><B>Результат</B></TD><TD ALIGN="CENTER"><B>Комментарий</B></TD></TR><TR><TD><PRE>http://example.com</PRE></TD><TD><A HREF="http://example.com">http://example.com</A></TD><TD>Ссылка на адрес в интернете</TD></TR><TR><TD><PRE>[[http://example.com]]</PRE></TD><TD><A HREF="http://example.com">http://example.com</A></TD><TD>Ссылка на адрес в интернете</TD></TR><TR><TD><PRE>[[Пример ссылки -&gt; http://example.com]]</PRE></TD><TD><A HREF="http://example.com">Пример ссылки</A></TD><TD>Ссылка на адрес в интернете с заданным текстом</TD></TR><TR><TD><PRE>[[http://example.com | Пример ссылки]]</PRE></TD><TD><A HREF="http://example.com">Пример ссылки</A></TD><TD>Ссылка на адрес в интернете с заданным текстом</TD></TR></TABLE>'''
	
		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testTable3 (self):
		text = u"""||border=1 width=350
||left aligned \\
sdfsdf || centered || right aligned||
||left aligned [[<<]] dsfsdf || centered || right aligned||
||left aligned [[&lt;&lt;]] dsfsdf || centered || right aligned||
||left aligned [[<<]][[<<]] sdfsdfsdf || centered || right aligned||
"""
		
		result = u'''<TABLE border=1 width=350><TR><TD ALIGN="LEFT">left aligned sdfsdf</TD><TD ALIGN="CENTER">centered</TD><TD ALIGN="RIGHT">right aligned</TD></TR><TR><TD ALIGN="LEFT">left aligned <BR> dsfsdf</TD><TD ALIGN="CENTER">centered</TD><TD ALIGN="RIGHT">right aligned</TD></TR><TR><TD ALIGN="LEFT">left aligned <BR> dsfsdf</TD><TD ALIGN="CENTER">centered</TD><TD ALIGN="RIGHT">right aligned</TD></TR><TR><TD ALIGN="LEFT">left aligned <BR><BR> sdfsdfsdf</TD><TD ALIGN="CENTER">centered</TD><TD ALIGN="RIGHT">right aligned</TD></TR></TABLE>'''
	
		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testBoldSubscript (self):
		text = u"бла-бла-бла '''x'_c_'''' бла-бла-бла"
		result = u'бла-бла-бла <B>x<SUB>c</SUB></B> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testSubscriptBold (self):
		text = u"бла-бла-бла '_'''xc'''_' бла-бла-бла"
		result = u'бла-бла-бла <SUB><B>xc</B></SUB> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testBoldSuperscript (self):
		text = u"бла-бла-бла '''x'^c^'''' бла-бла-бла"
		result = u'бла-бла-бла <B>x<SUP>c</SUP></B> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testSuperscriptBold (self):
		text = u"бла-бла-бла '^'''xc'''^' бла-бла-бла"
		result = u'бла-бла-бла <SUP><B>xc</B></SUP> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	
	
	def testSubscriptBold (self):
		text = u"бла-бла-бла '_'''xc'''_' бла-бла-бла"
		result = u'бла-бла-бла <SUB><B>xc</B></SUB> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testSuperscriptBold (self):
		text = u"бла-бла-бла '^'''xc'''^' бла-бла-бла"
		result = u'бла-бла-бла <SUP><B>xc</B></SUP> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testItalicSubscript (self):
		text = u"бла-бла-бла ''x'_c_''' бла-бла-бла"
		result = u'бла-бла-бла <I>x<SUB>c</SUB></I> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testItalicSuperscript (self):
		text = u"бла-бла-бла ''x'^c^''' бла-бла-бла"
		result = u'бла-бла-бла <I>x<SUP>c</SUP></I> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testBoldItalicSubscript (self):
		text = u"бла-бла-бла ''''x'_c_''''' бла-бла-бла"
		result = u'бла-бла-бла <B><I>x<SUB>c</SUB></I></B> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testBoldItalicSuperscript (self):
		text = u"бла-бла-бла ''''x'^c^''''' бла-бла-бла"
		result = u'бла-бла-бла <B><I>x<SUP>c</SUP></I></B> бла-бла-бла'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testUrlParse1 (self):
		text = u"http://example.com/,"
		result = u'<A HREF="http://example.com/">http://example.com/</A>,'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUrlParse2 (self):
		text = u"http://example.com/."
		result = u'<A HREF="http://example.com/">http://example.com/</A>.'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testUrlParse3 (self):
		text = u"http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz),"
		result = u'<A HREF="http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)">http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)</A>,'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUrlParse4 (self):
		text = u"http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)."
		result = u'<A HREF="http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)">http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)</A>.'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUrlParse5 (self):
		text = u"http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/,"
		result = u'<A HREF="http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/">http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/</A>,'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testUrlParse6 (self):
		text = u"http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/."
		result = u'<A HREF="http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/">http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/</A>.'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testUrlParse7 (self):
		text = u"http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/"
		result = u'<A HREF="http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/">http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/</A>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))

	
	def testUrlParse8 (self):
		text = u"http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/"
		result = u'<A HREF="http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/">http://ru.wikipedia.org/wiki/xxx,_yyy_(zzz)/</A>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUrlParse9 (self):
		text = u"www.jenyay.net"
		result = u'<A HREF="http://www.jenyay.net">www.jenyay.net</A>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))
	

	def testUrlParse10 (self):
		text = u"www.jenyay.net,"
		result = u'<A HREF="http://www.jenyay.net">www.jenyay.net</A>,'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testUrlParse11 (self):
		text = u"www.jenyay.net."
		result = u'<A HREF="http://www.jenyay.net">www.jenyay.net</A>.'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testUrlParse12 (self):
		text = u"www.jenyay.net/"
		result = u'<A HREF="http://www.jenyay.net/">www.jenyay.net/</A>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testUrlParse9 (self):
		text = u"ftp.jenyay.net"
		result = u'<A HREF="http://ftp.jenyay.net">ftp.jenyay.net</A>'

		self.assertEqual (self.parser.toHtml (text), result, self.parser.toHtml (text).encode (self.encoding))


	def testLineBreak1 (self):
		text = u"Строка 1[[<<]]Строка 2"
		result_right = u"Строка 1<BR>Строка 2"
		result = self.parser.toHtml (text)

		self.assertEqual (result, result_right, result)
	

	def testLineBreak2 (self):
		text = u"Строка 1[[&lt;&lt;]]Строка 2"
		result_right = u"Строка 1<BR>Строка 2"
		result = self.parser.toHtml (text)

		self.assertEqual (result, result_right, result)


	def testLineBreak3 (self):
		text = u"Строка 1\\\nСтрока 2"
		result_right = u"Строка 1Строка 2"
		result = self.parser.toHtml (text)

		self.assertEqual (result, result_right, result)

	
	def testLineBreak4 (self):
		text = ur"""# Первый элемент списка.
# Второй элемент списка [[<<]]Вторая строка второго элемента списка.
# Третий элемент списка [[<<]][[<<]] Вторая строка третьего элемента списка после двух отступов.
# Четвертый элемент списка."""

		result_right = ur"""<OL><LI>Первый элемент списка.</LI><LI>Второй элемент списка <BR>Вторая строка второго элемента списка.</LI><LI>Третий элемент списка <BR><BR> Вторая строка третьего элемента списка после двух отступов.</LI><LI>Четвертый элемент списка.</LI></OL>"""
		result = self.parser.toHtml (text)

		self.assertEqual (result, result_right, result)


	def testLineBreak5 (self):
		text = ur"""|| border=1
||Первая строка||
||Вторая строка [[<<]]продолжение второй строки||
||Третья строка [[<<]][[<<]] Продолжение третьей строки ||
||Четвертая \
строка ||"""

		result_right = ur"""<TABLE border=1><TR><TD>Первая строка</TD></TR><TR><TD>Вторая строка <BR>продолжение второй строки</TD></TR><TR><TD ALIGN="LEFT">Третья строка <BR><BR> Продолжение третьей строки</TD></TR><TR><TD ALIGN="LEFT">Четвертая строка</TD></TR></TABLE>"""
		result = self.parser.toHtml (text)

		self.assertEqual (result, result_right, result)


	def testTex1 (self):
		thumb = Thumbnails (self.parser.page)
		texrender = getTexRender(thumb.getThumbPath (True))

		eqn = "y = f(x)"
		text = "{$ %s $}" % (eqn)

		fname = texrender.getImageName (eqn)
		path = os.path.join (Thumbnails.getRelativeThumbDir(), fname)

		result_right = u'<IMG SRC="{0}">'.format (path)

		result = self.parser.toHtml (text)

		self.assertEqual (result_right, result, result)

		full_path = os.path.join (self.parser.page.path, path)
		self.assertTrue (os.path.exists (full_path), full_path )


	def testTex2 (self):
		thumb = Thumbnails (self.parser.page)
		texrender = getTexRender(thumb.getThumbPath (True))

		eqn1 = "y = f(x)"
		eqn2 = "y = e^x"
		eqn3 = "y = \sum_{i=0}\pi"

		text = u"""бла-бла-бла
* бла-бла-бла {$ %s $} 1111
* бла-бла-бла {$ %s $} 222
* бла-бла-бла {$ %s $} 333""" % (eqn1, eqn2, eqn3)

		fname1 = texrender.getImageName (eqn1)
		fname2 = texrender.getImageName (eqn2)
		fname3 = texrender.getImageName (eqn3)

		path1 = os.path.join (Thumbnails.getRelativeThumbDir(), fname1)
		path2 = os.path.join (Thumbnails.getRelativeThumbDir(), fname2)
		path3 = os.path.join (Thumbnails.getRelativeThumbDir(), fname3)

		result_right = u'''бла-бла-бла
<UL><LI>бла-бла-бла <IMG SRC="{path1}"> 1111</LI><LI>бла-бла-бла <IMG SRC="{path2}"> 222</LI><LI>бла-бла-бла <IMG SRC="{path3}"> 333</LI></UL>'''.format (**locals())


		result = self.parser.toHtml (text)

		self.assertEqual (result_right, result, result)

		full_path1 = os.path.join (self.parser.page.path, path1)
		full_path2 = os.path.join (self.parser.page.path, path2)
		full_path3 = os.path.join (self.parser.page.path, path3)

		self.assertTrue (os.path.exists (full_path1), full_path1)
		self.assertTrue (os.path.exists (full_path2), full_path2)
		self.assertTrue (os.path.exists (full_path3), full_path3)


	def testTex3 (self):
		thumb = Thumbnails (self.parser.page)
		texrender = getTexRender(thumb.getThumbPath (True))

		eqn = "y = f(x)"
		text = "[[{$ %s $} -> http://jenyay.net]]" % (eqn)

		fname = texrender.getImageName (eqn)
		path = os.path.join (Thumbnails.getRelativeThumbDir(), fname)

		result_right = u'<A HREF="http://jenyay.net"><IMG SRC="{0}"></A>'.format (path)

		result = self.parser.toHtml (text)

		self.assertEqual (result_right, result, result)

		full_path = os.path.join (self.parser.page.path, path)
		self.assertTrue (os.path.exists (full_path), full_path )


	def testTex4 (self):
		thumb = Thumbnails (self.parser.page)
		texrender = getTexRender(thumb.getThumbPath (True))

		eqn = "y = f(x)"
		text = "[[http://jenyay.net | {$ %s $}]]" % (eqn)

		fname = texrender.getImageName (eqn)
		path = os.path.join (Thumbnails.getRelativeThumbDir(), fname)

		result_right = u'<A HREF="http://jenyay.net"><IMG SRC="{0}"></A>'.format (path)

		result = self.parser.toHtml (text)

		self.assertEqual (result_right, result, result)

		full_path = os.path.join (self.parser.page.path, path)
		self.assertTrue (os.path.exists (full_path), full_path )


	def testCommandTest1 (self):
		self.parser.addCommand (TestCommand (self.parser))
		text = u"""(: test Параметр1 Параметр2=2 Параметр3=3 :)
Текст внутри
команды
(:testend:)"""

		result_right = u"""Command name: test
params: Параметр1 Параметр2=2 Параметр3=3
content: Текст внутри
команды"""

		result = self.parser.toHtml (text)
		self.assertEqual (result_right, result, result)


	def testCommandTest2 (self):
		command = TestCommand (self.parser)
		params = u"Параметр1 Параметр2=2 Параметр3=3"
		content = u"""Текст внутри
команды"""

		self.assertEqual (command.name, u"test")

		result = command.execute (params, content)
		result_right = u"""Command name: test
params: Параметр1 Параметр2=2 Параметр3=3
content: Текст внутри
команды"""

		self.assertEqual (result_right, result, result)


	def testCommandTest3 (self):
		self.parser.addCommand (TestCommand (self.parser))
		text = u"""(: test Параметр1 Параметр2=2 Параметр3=3 :)"""

		result_right = u"""Command name: test
params: Параметр1 Параметр2=2 Параметр3=3
content: """

		result = self.parser.toHtml (text)
		self.assertEqual (result_right, result, result)


	def testCommandTest4 (self):
		self.parser.addCommand (TestCommand (self.parser))
		text = u"""(:test:)"""

		result_right = u"""Command name: test
params: 
content: """

		result = self.parser.toHtml (text)
		self.assertEqual (result_right, result, result)


	def testCommandTest4 (self):
		self.parser.addCommand (TestCommand (self.parser))
		text = u"""(: test Параметр1 Параметр2=2 Параметр3=3 :)"""

		result_right = u"""Command name: test
params: Параметр1 Параметр2=2 Параметр3=3
content: """

		result = self.parser.toHtml (text)
		self.assertEqual (result_right, result, result)


	def testCommandTest4 (self):
		self.parser.addCommand (TestCommand (self.parser))
		text = u"""(: test Параметр1 Параметр2=2 Параметр3=3 :)
Текст внутри
команды
(:testend:)

(: test Параметры :)
Контент
(:testend:)"""

		result_right = u"""Command name: test
params: Параметр1 Параметр2=2 Параметр3=3
content: Текст внутри
команды

Command name: test
params: Параметры
content: Контент"""

		result = self.parser.toHtml (text)
		self.assertEqual (result_right, result, result)


	def testCommandTest5 (self):
		factory = ParserFactory ()
		factory.appendCommand (TestCommand)

		parser = factory.make (self.testPage, Application.config)

		
		text = u"""(: test Параметр1 Параметр2=2 Параметр3=3 :)
Текст внутри
команды
(:testend:)

(: test Параметры :)
Контент
(:testend:)"""

		result_right = u"""Command name: test
params: Параметр1 Параметр2=2 Параметр3=3
content: Текст внутри
команды

Command name: test
params: Параметры
content: Контент"""

		result = parser.toHtml (text)
		self.assertEqual (result_right, result, result)



	def testInvalidCommandTest (self):
		text = u"""(: testblabla Параметр1 Параметр2=2 Параметр3=3 :)
Текст внутри
команды
(:testend:)"""

		result_right = u"""(: testblabla Параметр1 Параметр2=2 Параметр3=3 :)
Текст внутри
команды
(:testend:)"""

		result = self.parser.toHtml (text)
		self.assertEqual (result_right, result, result)


	def testExceptionCommand (self):
		factory = ParserFactory ()
		factory.appendCommand (ExceptionCommand)

		parser = factory.make (self.testPage, Application.config)

		text = u"""(:exception:)"""

		result = parser.toHtml(text)
		# Исключение не должно бросаться, а должно быть выведено в результирующий текст
		self.assertTrue ("Exception" in result, result)
