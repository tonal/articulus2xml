# -*- codong: utf-8 -*-
from datetime import datetime
import logging
from pathlib import Path
from tempfile import gettempdir

from lxml import etree
from natsort import natsort_keygen


def construct_dir_source(dir_name, tmp_dir):
  # self_path = Path(__file__)
  self_path = Path('.')
  root = etree.Element('files')
  parser = etree.HTMLParser()
  if not tmp_dir or tmp_dir == '-':
    tmp_dir = gettempdir()
    logging.debug(
      'Путь к каталогу для временноых файлов установлен в "%s"', tmp_dir)
  tmp_dir = Path(tmp_dir)
  if not tmp_dir.exists():
    old_p = tmp_dir
    tmp_dir = gettempdir()
    logging.debug(
      'Путь к каталогу для временноых файлов установлен в "%s", '
      'т. к. указанный путь "%s" не существует',
      tmp_dir, old_p)
    tmp_dir = Path(tmp_dir)
  title_exists = False
  files = tuple(sorted(
    (f for f in Path(dir_name).glob('*.html') if f.is_file()),
    key=natsort_keygen()))
  for fparh in files:
    tfile:Path = tmp_dir / fparh.name
    with tfile.open('wb') as fout:
      src_root = etree.parse(fparh.as_posix(), parser)
      fout.write(
        etree.tostring(src_root, pretty_print=True, encoding='utf-8'))
    if fparh.name.lower() == 'title.html':
      title_exists = True
      tag = 'title'
    else:
      tag = 'issue'
    file_uri = tfile.as_uri() if tfile.is_absolute() else tfile.as_posix()
    etree.SubElement(root, tag, path=file_uri)
  logging.debug(etree.tostring(root, pretty_print=True, encoding='unicode'))
  if not title_exists:
    logging.error(
      'В составе файлов не обнаружили title.html: %s',
      tuple(f.resolve().as_posix() for f in  files))
    raise SystemExit(1)
  return root


def soran_transform_dir(
  dir_name, oname:str, out_dir:str, codeNEB:str, temp_path:str
):
  src_root = construct_dir_source(dir_name, temp_path)

  ns = etree.FunctionNamespace('http://promsoft.ru/soran_transform/dir')
  ns.prefix = 'ps'

  journal = JornalParser(ns)

  parser = etree.XMLParser(no_network=True)
  parser.resolvers.add(FileResolver())

  xslt = etree.XML(XSLT, parser)
  # xslt = etree.parse('convert_dir.xslt', parser)
  transform = etree.XSLT(xslt)
  parser = etree.HTMLParser()
  # src_root = etree.parse(iname, parser)
  # res_trans = transform(src_root, params=etree.XSLT.strparam(openstat))
  res_trans = transform(src_root)
  if oname == '-':
    print(res_trans)
    return

  if not oname:
    if not codeNEB:
      codeNEB = journal.codeNEB
    oname = f'{codeNEB}_{datetime.now().date().isoformat()}_unicode.xml'
  opath = Path(out_dir) / oname if out_dir else Path(oname)
  with opath.open('wt', encoding='utf-8') as out:
    out.write('%s' % res_trans)

  logging.info('Создан файл: %s', opath)

  return opath


class FileResolver(etree.Resolver):
  def resolve(self, url, pubid, context):
    # print(url)
    return self.resolve_filename(url, context)


class JornalParser:

  codeNEB:str = None

  def __init__(self, ns):
    ns['get_pid'] = self.get_pid
    ns['get_codeNEB'] = self.get_codeNEB
    ns['ends-with'] = self.ends_with
    ns['now'] = self.now

  def get_pid(self, _, e):
    tid = e[0].text.split()[1]
    return tid

  def get_codeNEB(self, _, e):
    issn = e[0].text.strip()
    self.codeNEB = codeNEB = ''.join(c for c in issn if c.isdigit())
    return codeNEB

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
  xmlns:ps="http://promsoft.ru/soran_transform/dir"
  exclude-result-prefixes="ps"
>
  <xsl:output
    omit-xml-declaration="no"
    encoding="utf-8"
    indent="yes"
  />
  <xsl:strip-space elements="*"/>
  <xsl:variable name="files" select="document(files/issue/@path)"/>
  <xsl:variable name="title_doc" select="document(files/title/@path)[1]"/>

  <xsl:template match="/">
    <journal>
      <operCard>
        <operator>Articulus_142</operator>
        <pid><xsl:value-of
          select="ps:get_pid($title_doc//div[@id='projectNumber']/span[1])"/></pid>
        <date><xsl:value-of select="ps:now()"/></date>
        <cntArticle><xsl:value-of
         select="count($files//div[@id='left']/ul[@class='Container']/li)"/></cntArticle>
        <cntNode/>
        <cs>0</cs>
      </operCard>
      <xsl:call-template name="title_jour" >
        <xsl:with-param name="title" select="$title_doc"/>
      </xsl:call-template>
      <issue>
        <xsl:call-template name="title_issue" >
          <xsl:with-param name="title" select="$title_doc"/>
        </xsl:call-template>
        <articles>
        <xsl:for-each select="$files//div[@id='left']/ul[@class='Container']/li">
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
              <xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Коды']/ul[@class='Container']/li">
                <xsl:if test="div/a/text() = 'УДК'">
                <udk><xsl:value-of select="ul[@class='Container']/li/div/p"/></udk>
                </xsl:if>
                <xsl:if test="div/a/text() = 'DOI'">
                <doi><xsl:value-of select="ul[@class='Container']/li/div/p"/></doi>
                </xsl:if>
              </xsl:for-each>
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
            <xsl:if test="ul[@class='Container']/li[div/a/text() = 'Финансирование']">
            <artFunding><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Финансирование']/ul[@class='Container']/li">
              <funding lang="{substring(@id, 5)}"><xsl:value-of select="ul[@class='Container']/li/div/p"/></funding>
            </xsl:for-each></artFunding>
            </xsl:if>
            <dates><xsl:for-each select="ul[@class='Container']/li[div/a/text() = 'Даты']/ul[@class='Container']/li">
              <dateReceived><xsl:value-of select="ul/li/div/p"/></dateReceived>
            </xsl:for-each></dates>
          </article >
        </xsl:for-each>
        </articles>
      </issue>

    </journal>
  </xsl:template>

  <!--xsl:template match="node() | @*" name="copy_all">
      <xsl:copy>
          <xsl:apply-templates select="node() | @*" />
      </xsl:copy>
  </xsl:template -->
  
  <xsl:template name="title_jour" mode="title">
    <xsl:param name="title"/>
    <titleid><xsl:value-of select="$title//p[@id='p000DAT']"/></titleid>
    <issn><xsl:value-of select="$title//p[@id='p001DAT']"/></issn>
    <codeNEB><xsl:value-of select="ps:get_codeNEB($title//p[@id='p001DAT'])"/></codeNEB>
    <xsl:for-each select="$title//li[@id='n005']/ul/li">
    <journalInfo lang="{substring(@id, 5)}">
      <title><xsl:value-of select="ul/li/div[@class='Content']/p"/></title>
    </journalInfo>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="title_issue" mode="title">
    <xsl:param name="title"/>
    <volume><xsl:value-of select="$title//p[@id='p006DAT']"/></volume>
    <number><xsl:value-of select="$title//p[@id='p007DAT']"/></number>
    <altNumber/>
    <part/>
    <dateUni><xsl:value-of select="$title//p[@id='p031DAT']"/></dateUni>
    <issTitle/>
    <pages><xsl:value-of select="$title//p[@id='p013DAT']"/></pages>
  </xsl:template>
  
</xsl:stylesheet>
'''