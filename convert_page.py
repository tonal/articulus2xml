# -*- codong: utf-8 -*-
from datetime import datetime

from lxml import etree


def soran_transform_page(iname, oname):
  ns = etree.FunctionNamespace('http://promsoft.ru/soran_transform/page')
  ns.prefix = 'ps'
  journal = JornalParser(ns)
  xslt = etree.XML(XSLT)
  transform = etree.XSLT(xslt)
  parser = etree.HTMLParser()
  src_root = etree.parse(iname, parser)
  # res_trans = transform(src_root, params=etree.XSLT.strparam(openstat))
  res_trans = transform(src_root)
  open(oname, 'wt', encoding='utf-8').write('%s' % res_trans)


class JornalParser:

  root = None

  def __init__(self, ns):
    ns['parse_journal_info'] = self.set_elts
    ns['get_pid'] = self.get_pid
    ns['get_titleid'] = self.get_titleid
    ns['get_issn'] = self.get_issn
    ns['get_title'] = self.get_title
    ns['get_dateUni'] = self.get_dateUni
    ns['get_volume'] = self.get_volume
    ns['get_number'] = self.get_number
    ns['get_pages'] = self.get_pages
    ns['ends-with'] = self.ends_with
    ns['now'] = self.now

  def set_elts(self, _, e):
    assert e, f'Нет информации о журнале: {e}'
    self.root = e[0]

  def get_pid(self, _):
    tid = self.root.xpath(
      'div[@id="projectNumber"]/span[1]')[0].text.split()[1]
    return tid

  def get_titleid(self, _):
    tid = self.root.xpath(
      'div[@id="projectNumber"]/span[1]')[0].text.split()[1]
    return tid

  def get_issn(self, _):
    issn = self.root.xpath('div[2]/b[1]')[0].text
    return issn

  def get_title(self, _):
    title = self.root.xpath('div[2]/b[1]')[0].tail.strip()
    title = title.strip(',').strip()
    return title

  def get_dateUni(self, _):
    du = self.root.xpath('div[2]/b[2]')[0].text
    return du

  def get_volume(self, _):
    volume = self.root.xpath('div[2]/b[3]')[0].text
    return volume

  def get_number(self, _):
    number = self.root.xpath('div[2]/b[4]')[0].text
    return number

  def get_pages(self, _):
    pages = self.root.xpath('div[2]/b[4]')[0].tail.strip()
    pages = pages.split()[-1]
    return pages

  def ends_with(self, _, s, *args):
    if not s:
      return False
    if not isinstance(s, str):
      s = s[0]
    return s.endswith(args)

  def now(self, _):
    dt = datetime.now().replace(microsecond=0)
    return dt.isoformat(' ')


# language=XML
XSLT = '''<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ps="http://promsoft.ru/yml2vk_filter"
  exclude-result-prefixes="ps"
>
  <xsl:output
    omit-xml-declaration="no"
    encoding="utf-8"
    indent="yes"
  />
  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <journal>
      <xsl:value-of select="ps:parse_journal_info(//div[@id='caption'])"/>
      <operCard>
        <operator>Articulus_142</operator>
        <pid><xsl:value-of select="ps:get_pid()"/></pid>
        <date><xsl:value-of select="ps:now()"/></date>
        <cntArticle><xsl:value-of 
         select="count(//div[@id='left']/ul[@class='Container']/li)"/></cntArticle>
        <cntNode/>
        <cs>0</cs>
      </operCard>
      <titleid><xsl:value-of select="ps:get_titleid()"/></titleid>
      <issn><xsl:value-of select="ps:get_issn()"/></issn>
      <journalInfo lang="RUS">
        <title><xsl:value-of select="ps:get_title()"/></title>
      </journalInfo>
      <issue>
        <volume><xsl:value-of select="ps:get_volume()"/></volume>
        <number><xsl:value-of select="ps:get_number()"/></number>
        <altNumber/>
        <part/>
        <dateUni><xsl:value-of select="ps:get_dateUni()"/></dateUni>
        <issTitle/>
        <pages><xsl:value-of select="ps:get_pages()"/></pages>
        <articles><xsl:for-each select="//div[@id='left']/ul[@class='Container']/li">
          <article>
            <pages><xsl:value-of
             select="ul[@class='Container']/li[div/a/text() = 'Страницы']/ul/li/div[@class='Content']/p[@id]"/></pages>
            <artType><xsl:value-of
             select="ul[@class='Container']/li[div/a/text() = 'Тип статьи']/ul/li/div[@class='Content']/p[@id]"/></artType>
            <authors><xsl:for-each 
             select="ul[@class='Container']/li[div/a/text() = 'Авторы']/ul[@class='Container']/li">
              <author num="{position()}"><xsl:for-each select="ul[@class='Container']/li">
                <individInfo lang="{substring(@id, 8)}">
                  <surname><xsl:value-of 
                   select="ul[@class='Container']/li[div/a[@id]/text() = 'Фамилия']/ul/li/div[@class='Content']/p[@id]"/></surname>
                  <initials><xsl:value-of 
                   select="ul[@class='Container']/li[div/a[@id]/text() = 'Имя Отчество']/ul/li/div[@class='Content']/p[@id]"/></initials>
                  <xsl:if test="ul[@class='Container']/li/div/a[@id]/text() = 'Место работы'">
                  <orgName><xsl:value-of 
                   select="ul[@class='Container']/li[div/a[@id]/text() = 'Место работы']/ul/li/div[@class='Content']/p[@id]"/></orgName>
                  </xsl:if>
                  <xsl:if test="ul[@class='Container']/li/div/a[@id]/text() = 'Город, Страна'">
                  <address><xsl:value-of 
                   select="ul[@class='Container']/li[div/a[@id]/text() = 'Город, Страна']/ul/li/div[@class='Content']/p[@id]"/></address>
                  </xsl:if>
                  <xsl:if test="ul[@class='Container']/li/div/a[@id]/text() = 'Email'">
                  <email><xsl:value-of 
                   select="ul[@class='Container']/li[div/a[@id]/text() = 'Email']/ul/li/div[@class='Content']/p[@id]"/></email>
                  </xsl:if>
                </individInfo>
              </xsl:for-each></author>
            </xsl:for-each></authors>
            <artTitles><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Заглавие']/ul[@class='Container']/li">
              <artTitle lang="{substring(@id, 5)}"><xsl:copy-of select="ul/li/div[@class='Content']/p/node()"/></artTitle>
            </xsl:for-each></artTitles>
            <abstracts><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Аннотация']/ul[@class='Container']/li">
              <abstract lang="{substring(@id, 5)}"><xsl:copy-of select="ul/li/div[@class='Content']/p/node()"/></abstract>
            </xsl:for-each></abstracts>
            <xsl:for-each 
             select="ul[@class='Container']/li[div/a/text() = 'Текст']/ul[@class='Container']/li[ps:ends-with(@id, 'RUS', 'ENG')]">
            <text lang="{substring(@id, 5)}"><xsl:copy-of select="ul/li/div[@class='Content']/p/node()"/></text>
            </xsl:for-each>
            <codes>
              <xsl:if 
               test="ul[@class='Container']/li[div/a/text() = 'Текст']/ul[@class='Container']/li[div/a/text()='DOI']">
              <doi><xsl:value-of 
               select="ul[@class='Container']/li[div/a/text() = 'Текст']/ul[@class='Container']/li[div/a/text()='DOI']/ul/li/div/p"/></doi>
              </xsl:if>
            </codes>
            <keywords><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Ключевые слова']/ul[@class='Container']/li">
              <kwdGroup lang="{substring(@id, 5)}"><xsl:for-each select="ul[@class='Container']/li">
                <keyword><xsl:copy-of select="div[@class='Content']/p/node()"/></keyword>
              </xsl:for-each></kwdGroup>
            </xsl:for-each></keywords>
            <references><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Ссылки']/ul[@class='Container']/li">
              <reference><xsl:value-of select="position()"/>. <xsl:copy-of select="div[@class='Content']/p/node()"/></reference>
            </xsl:for-each></references>
            <files><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Файлы']/ul[@class='Container']/li">
              <file><xsl:value-of select="div[@class='Content']/p"/></file>
            </xsl:for-each></files>
            <artFunding><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Финансирование']/ul[@class='Container']/li">
              <funding lang="{substring(@id, 5)}"><xsl:value-of select="ul[@class='Container']/li/div/p"/></funding>
            </xsl:for-each></artFunding>
            <dates><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Даты']/ul[@class='Container']/li">
              <dateReceived><xsl:value-of 
                select="ul/li/div/p"/></dateReceived>
            </xsl:for-each></dates>
          </article>
        </xsl:for-each></articles>
      </issue>
       
    </journal>
  </xsl:template>

  <xsl:template match="node() | @*" name="copy_all">
      <xsl:copy>
          <xsl:apply-templates select="node() | @*" />
      </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>
'''
