<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:fo="http://www.w3.org/1999/XSL/Format">
  <xsl:template match="/">
    <fo:root>
      <fo:layout-master-set>
        <fo:simple-page-master master-name="A4" page-height="11in" page-width="8.5in" margin="1in">
          <fo:region-body/>
        </fo:simple-page-master>
      </fo:layout-master-set>
      <fo:page-sequence master-reference="A4">
        <fo:flow flow-name="xsl-region-body">
          <fo:block font-size="16pt" font-weight="bold" margin-bottom="0.5in">Book List</fo:block>
          <xsl:for-each select="bookstore/book">
            <fo:block>
              <fo:inline font-weight="bold">Title: </fo:inline><xsl:value-of select="title"/>
            </fo:block>
            <fo:block>
              <fo:inline font-weight="bold">Author: </fo:inline><xsl:value-of select="author"/>
            </fo:block>
            <fo:block margin-bottom="0.2in"/>
          </xsl:for-each>
        </fo:flow>
      </fo:page-sequence>
    </fo:root>
  </xsl:template>
</xsl:stylesheet>