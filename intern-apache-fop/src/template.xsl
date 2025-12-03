<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
      xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:fo="http://www.w3.org/1999/XSL/Format">
  
  <!-- Main template -->
  <xsl:template match="/">
    <fo:root>
      <fo:layout-master-set>
        <!-- Page layout for A4 -->
        <fo:simple-page-master master-name="A4" 
                               page-height="11in" 
                               page-width="8.5in" 
                               margin-top="0.75in" 
                               margin-bottom="0.75in" 
                               margin-left="1in" 
                               margin-right="1in">
          <fo:region-body margin-bottom="0.5in"/>
          <fo:region-after extent="0.5in"/>
        </fo:simple-page-master>
      </fo:layout-master-set>
      
      <fo:page-sequence master-reference="A4">
        <!-- Title Page -->
        <fo:flow flow-name="xsl-region-body">
          <xsl:apply-templates select="book"/>
        </fo:flow>
      </fo:page-sequence>
    </fo:root>
  </xsl:template>
  
  <!-- Book template -->
  <xsl:template match="book">
    <!-- Title Page -->
    <fo:block font-size="24pt" font-weight="bold" text-align="center" 
              space-after="0.5in" margin-top="3in">
      <xsl:value-of select="@title"/>
    </fo:block>
    
    <fo:block font-size="12pt" text-align="center" space-after="0.3in">
      <xsl:value-of select="metadata/author"/>
    </fo:block>
    
    <fo:block font-size="10pt" text-align="center" space-after="0.2in">
      <xsl:value-of select="metadata/publisher"/>
    </fo:block>
    
    <fo:block font-size="9pt" text-align="center" space-after="0.2in">
      <xsl:value-of select="metadata/date"/>
    </fo:block>
    
    <fo:block font-size="9pt" text-align="center" space-after="2in">
      ISBN: <xsl:value-of select="metadata/isbn"/>
    </fo:block>
    
    <!-- Page break -->
    <fo:block break-after="page"/>
    
    <!-- Chapters -->
    <xsl:apply-templates select="chapter"/>
  </xsl:template>
  
  <!-- Chapter template -->
  <xsl:template match="chapter">
    <fo:block font-size="20pt" font-weight="bold" 
              space-before="0.5in" space-after="0.3in" 
              keep-with-next="always">
      Chapter <xsl:number value="position()"/>: <xsl:value-of select="@title"/>
    </fo:block>
    
    <!-- Chapter intro -->
    <xsl:if test="intro">
      <fo:block font-size="11pt" font-style="italic" 
                space-after="0.3in" margin-left="0.2in">
        <xsl:apply-templates select="intro/para"/>
      </fo:block>
    </xsl:if>
    
    <!-- Sections -->
    <xsl:apply-templates select="section"/>
  </xsl:template>
  
  <!-- Section template -->
  <xsl:template match="section">
    <fo:block font-size="16pt" font-weight="bold" 
              space-before="0.4in" space-after="0.2in" 
              keep-with-next="always"
              margin-left="0.2in">
      <xsl:value-of select="@title"/>
    </fo:block>
    
    <!-- Subjects -->
    <xsl:apply-templates select="subject"/>
  </xsl:template>
  
  <!-- Subject template -->
  <xsl:template match="subject">
    <fo:block font-size="14pt" font-weight="bold" 
              space-before="0.3in" space-after="0.15in" 
              margin-left="0.4in" 
              color="#333333">
      <xsl:value-of select="@name"/>
    </fo:block>
    
    <!-- Pageblocks -->
    <xsl:apply-templates select="pageblock"/>
  </xsl:template>
  
  <!-- Pageblock template -->
  <xsl:template match="pageblock">
    <fo:block space-before="0.2in" space-after="0.2in" margin-left="0.6in">
      <!-- Heading -->
      <xsl:if test="heading">
        <fo:block font-size="13pt" font-weight="bold" 
                  space-after="0.1in" 
                  color="#0066CC">
          <xsl:value-of select="heading"/>
        </fo:block>
      </xsl:if>
      
      <!-- Text pageblock -->
      <xsl:if test="@type='text'">
        <xsl:apply-templates select="para"/>
      </xsl:if>
      
      <!-- Task pageblock -->
      <xsl:if test="@type='task'">
        <xsl:apply-templates select="task"/>
      </xsl:if>
    </fo:block>
  </xsl:template>
  
  <!-- Task template -->
  <xsl:template match="task">
    <fo:block space-after="0.15in">
      <!-- Task description -->
      <xsl:if test="description">
        <fo:block font-size="11pt" font-style="italic" 
                  space-after="0.15in" 
                  margin-left="0.2in">
          <xsl:value-of select="description"/>
        </fo:block>
      </xsl:if>
      
      <!-- Task level badge -->
      <xsl:if test="@level">
        <fo:block font-size="9pt" space-after="0.1in" margin-left="0.2in">
          <fo:inline font-weight="bold">Level: </fo:inline>
          <fo:inline background-color="#E6F3FF" 
                     padding="2pt 6pt">
            <xsl:value-of select="@level"/>
          </fo:inline>
        </fo:block>
      </xsl:if>
      
      <!-- Steps -->
      <fo:block space-before="0.15in" space-after="0.15in" margin-left="0.3in">
        <xsl:apply-templates select="step"/>
      </fo:block>
      
      <!-- Expected Result -->
      <xsl:if test="expectedResult">
        <fo:block font-size="10pt" 
                  space-before="0.15in" 
                  space-after="0.1in" 
                  margin-left="0.2in" 
                  padding="0.1in" 
                  background-color="#F0F8E6">
          <fo:inline font-weight="bold">Expected Result: </fo:inline>
          <xsl:value-of select="expectedResult"/>
        </fo:block>
      </xsl:if>
      
      <!-- Safety Warnings -->
      <xsl:if test="safetyWarnings">
        <fo:block font-size="10pt" 
                  space-before="0.15in" 
                  space-after="0.1in" 
                  margin-left="0.2in" 
                  padding="0.1in" 
                  background-color="#FFE6E6">
          <fo:inline font-weight="bold" color="#CC0000">⚠ Safety Warning: </fo:inline>
          <xsl:apply-templates select="safetyWarnings/warning"/>
        </fo:block>
      </xsl:if>
      
      <!-- Tools -->
      <xsl:if test="tools">
        <fo:block font-size="10pt" 
                  space-before="0.1in" 
                  space-after="0.1in" 
                  margin-left="0.2in">
          <fo:inline font-weight="bold">Required Tools: </fo:inline>
          <xsl:for-each select="tools/tool">
            <xsl:value-of select="."/>
            <xsl:if test="position() != last()">, </xsl:if>
          </xsl:for-each>
        </fo:block>
      </xsl:if>
      
      <!-- Estimated Time -->
      <xsl:if test="estimatedTime">
        <fo:block font-size="10pt" 
                  space-before="0.1in" 
                  space-after="0.15in" 
                  margin-left="0.2in">
          <fo:inline font-weight="bold">Estimated Time: </fo:inline>
          <xsl:value-of select="estimatedTime"/> 
          <xsl:value-of select="estimatedTime/@unit"/>
        </fo:block>
      </xsl:if>
    </fo:block>
  </xsl:template>
  
  <!-- Step template -->
  <xsl:template match="step">
    <fo:block font-size="11pt" 
              space-after="0.15in" 
              margin-left="0.2in" 
              text-indent="-0.2in" 
              padding-left="0.3in">
      <fo:inline font-weight="bold" color="#0066CC">
        Step <xsl:value-of select="@number"/>:
      </fo:inline>
      <fo:inline margin-left="0.1in">
        <xsl:value-of select="normalize-space(.)"/>
      </fo:inline>
    </fo:block>
  </xsl:template>
  
  <!-- Para template -->
  <xsl:template match="para">
    <fo:block font-size="11pt" 
              space-after="0.1in" 
              text-align="justify" 
              line-height="1.4">
      <xsl:value-of select="normalize-space(.)"/>
    </fo:block>
  </xsl:template>
  
  <!-- Warning template -->
  <xsl:template match="warning">
    <xsl:value-of select="normalize-space(.)"/>
    <xsl:if test="position() != last()">
      <fo:block/>
    </xsl:if>
  </xsl:template>
  
</xsl:stylesheet>
