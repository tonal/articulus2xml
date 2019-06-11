<?xml version="1.0"?>
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
      <titleid><xsl:value-of select="$title_doc//p[@id='p000DAT']"/></titleid>
      <issn><xsl:value-of select="$title_doc//p[@id='p001DAT']"/></issn>
      <codeNEB><xsl:value-of select="ps:get_codeNEB($title_doc//p[@id='p001DAT'])"/></codeNEB>
      <xsl:for-each select="$title_doc//li[@id='n005']/ul/li">
      <journalInfo lang="{substring(@id, 5)}">
        <title><xsl:value-of select="ul/li/div[@class='Content']/p"/></title>
      </journalInfo>
      </xsl:for-each>
      <issue>
        <volume><xsl:value-of select="$title_doc//p[@id='p006DAT']"/></volume>
        <number><xsl:value-of select="$title_doc//p[@id='p007DAT']"/></number>
        <altNumber/>
        <part/>
        <dateUni><xsl:value-of select="$title_doc//p[@id='p013DAT']"/></dateUni>
        <issTitle/>
        <pages><xsl:value-of select="$title_doc//p[@id='p031DAT']"/></pages>
        <articles><xsl:for-each select="$files//div[@id='left']/ul[@class='Container']/li">
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
