<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version="1.0">

  <!-- Parameters mapping ${...} variables from .lay -->
  <xsl:param name="logofile" select="'logo.png'"/>
  <xsl:param name="securityHeader" select="'SECURITY HEADER'"/>
  <xsl:param name="addInfoVar" select="'Additional Info'"/>
  <xsl:param name="pmc" select="'PMC CODE'"/>
  <xsl:param name="printTime" select="'Print Time'"/>
  <xsl:param name="inworkInfo" select="'In Work'"/>

  <xsl:param name="dmApplicVar" select="'Applicability text'"/>
  <xsl:param name="dmcIssnoLabelVar" select="'DMC/ISSNO label'"/>
  <xsl:param name="proprietaryTextVar" select="'Proprietary text'"/>
  <xsl:param name="endLabelPostfix" select="'END LABEL'"/>
  <xsl:param name="securityFooter" select="'SECURITY FOOTER'"/>
  <xsl:param name="dmDmCodeStringVar" select="'DMC CODE'"/>
  <xsl:param name="pnrtype" select="'ARABIC'"/>
  <xsl:param name="dmIssueDateYear" select="'0000'"/>
  <xsl:param name="dmIssueDateMonth" select="'00'"/>
  <xsl:param name="dmIssueDateDay" select="'00'"/>
  <xsl:param name="descTextVar" select="'Description'"/>
  <xsl:param name="procedTextVar" select="'Procedure'"/>
  <xsl:param name="dmDmc" select="''"/>
  <xsl:param name="titlePageImage" select="'titlepage-image.png'"/>
  <xsl:param name="manufacturerLogo" select="'manufacturer-logo.png'"/>
  <xsl:param name="manufacturerAddress" select="'Manufacturer address goes here'"/>
  <xsl:param name="renderTitlePage" select="'true'"/>
  <xsl:param name="pageMaster" select="'simpleA4'"/>

  <!-- Global variable: check if update highlight is enabled -->
  <!-- Change marks appear only when reasonForUpdate has updateHighlight="1" -->
  <xsl:variable name="isUpdateHighlighted"
                select="boolean(//reasonForUpdate[@updateHighlight='1'])"/>
  
  <!-- Get the reasonForUpdate ID that has updateHighlight="1" for reference -->
  <xsl:variable name="updateHighlightId" 
                select="//reasonForUpdate[@updateHighlight='1']/@id"/>

  <!-- Root template producing FO -->
  <xsl:template match="/">
    <fo:root>
      <!-- Masters -->
      <fo:layout-master-set>

        <!-- A4 Simple -->
        <fo:simple-page-master master-name="simpleA4"
                               page-width="210mm" page-height="297mm"
                               margin-left="25mm" margin-right="15mm"
                               margin-top="33mm" margin-bottom="30mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="25mm" precedence="true"/>
          <fo:region-after extent="25mm" precedence="true"/>
        </fo:simple-page-master>

        <!-- A4 CREW Right -->
        <fo:simple-page-master master-name="crewRightA4"
                               page-width="210mm" page-height="297mm"
                               margin-left="25mm" margin-right="15mm"
                               margin-top="33mm" margin-bottom="30mm">
          <fo:region-body margin-top="0mm" margin-bottom="0mm"/>
          <fo:region-before extent="30mm"/>
          <fo:region-after extent="30mm"/>
        </fo:simple-page-master>

        <!-- A4 CREW Left -->
        <fo:simple-page-master master-name="crewLeftA4"
                               page-width="210mm" page-height="297mm"
                               margin-left="25mm" margin-right="15mm"
                               margin-top="33mm" margin-bottom="30mm">
          <fo:region-body margin-top="0mm" margin-bottom="0mm"/>
          <fo:region-before extent="30mm"/>
          <fo:region-after extent="30mm"/>
        </fo:simple-page-master>

        <!-- A4 IPD First -->
        <fo:simple-page-master master-name="ipdFirstA4"
                               page-width="210mm" page-height="297mm"
                               margin-left="25mm" margin-right="15mm"
                               margin-top="33mm" margin-bottom="30mm">
          <fo:region-body margin-top="0mm" margin-bottom="0mm"/>
          <fo:region-before extent="30mm"/>
          <fo:region-after extent="30mm"/>
        </fo:simple-page-master>

        <!-- A4 Title page -->
        <fo:simple-page-master master-name="titleA4"
                               page-width="210mm" page-height="297mm"
                               margin-left="25mm" margin-right="15mm"
                               margin-top="33mm" margin-bottom="30mm">
          <fo:region-body margin-top="0mm" margin-bottom="0mm"/>
          <fo:region-before extent="30mm"/>
          <fo:region-after extent="30mm"/>
        </fo:simple-page-master>

        <!-- A3 Foldout -->
        <fo:simple-page-master master-name="foldoutA3"
                               page-width="420mm" page-height="297mm"
                               margin-left="25mm" margin-right="15mm"
                               margin-top="33mm" margin-bottom="31mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="25mm" precedence="true"/>
          <fo:region-after extent="25mm" precedence="true"/>
        </fo:simple-page-master>

        <!-- Letter Simple Right -->
        <fo:simple-page-master master-name="simpleLetterRight"
                               page-width="215.9mm" page-height="279.4mm"
                               margin-left="30mm" margin-right="15mm"
                               margin-top="25mm" margin-bottom="22mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="20mm" precedence="true"/>
          <fo:region-after extent="20mm" precedence="true"/>
        </fo:simple-page-master>

        <!-- Letter Simple Left -->
        <fo:simple-page-master master-name="simpleLetterLeft"
                               page-width="215.9mm" page-height="279.4mm"
                               margin-left="16mm" margin-right="29.9mm"
                               margin-top="25mm" margin-bottom="22mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="20mm" precedence="true"/>
          <fo:region-after extent="20mm" precedence="true"/>
        </fo:simple-page-master>

        <!-- Letter IPD First -->
        <fo:simple-page-master master-name="ipdFirstLetterRight"
                               page-width="215.9mm" page-height="279.4mm"
                               margin-left="30mm" margin-right="15mm"
                               margin-top="25mm" margin-bottom="22mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="20mm" precedence="true"/>
          <fo:region-after extent="20mm" precedence="true"/>
        </fo:simple-page-master>

        <!-- Letter IPD Simple Right -->
        <fo:simple-page-master master-name="ipdSimpleLetterRight"
                               page-width="215.9mm" page-height="279.4mm"
                               margin-left="30mm" margin-right="15mm"
                               margin-top="25mm" margin-bottom="22mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="20mm" precedence="true"/>
          <fo:region-after extent="20mm" precedence="true"/>
        </fo:simple-page-master>

        <!-- Letter IPD Simple Left -->
        <fo:simple-page-master master-name="ipdSimpleLetterLeft"
                               page-width="215.9mm" page-height="279.4mm"
                               margin-left="16mm" margin-right="29.9mm"
                               margin-top="25mm" margin-bottom="22mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="20mm" precedence="true"/>
          <fo:region-after extent="20mm" precedence="true"/>
        </fo:simple-page-master>

        <!-- Letter Foldout -->
        <fo:simple-page-master master-name="foldoutLetter"
                               page-width="431.8mm" page-height="279.4mm"
                               margin-left="30mm" margin-right="15mm"
                               margin-top="25mm" margin-bottom="22mm">
          <fo:region-body margin-top="5mm" margin-bottom="8mm"/>
          <fo:region-before extent="20mm" precedence="true"/>
          <fo:region-after extent="20mm" precedence="true"/>
        </fo:simple-page-master>

      </fo:layout-master-set>

      <!-- Bookmarks tree -->
      <fo:bookmark-tree>
        <xsl:if test="//description">
          <fo:bookmark internal-destination="description">
            <fo:bookmark-title><xsl:value-of select="$descTextVar"/></fo:bookmark-title>
          </fo:bookmark>
        </xsl:if>
        <xsl:if test="//mainProcedure">
          <fo:bookmark internal-destination="mainProc">
            <fo:bookmark-title><xsl:value-of select="$procedTextVar"/></fo:bookmark-title>
          </fo:bookmark>
        </xsl:if>
        <xsl:for-each select="//proceduralStep[title]">
          <fo:bookmark>
            <xsl:attribute name="internal-destination">
              <xsl:text>step-</xsl:text>
              <xsl:number level="multiple" count="proceduralStep" format="1.1.1.1"/>
            </xsl:attribute>
            <fo:bookmark-title>
              <xsl:number level="multiple" count="proceduralStep" format="1.1.1.1"/>
              <xsl:text> </xsl:text>
              <xsl:value-of select="normalize-space(title)"/>
            </fo:bookmark-title>
          </fo:bookmark>
        </xsl:for-each>
      </fo:bookmark-tree>

      <!-- Title Page - Disabled per user request -->
      <xsl:if test="false()">
        <fo:page-sequence master-reference="titleA4"
                          font-family="Helvetica" font-size="10pt" line-height="12pt"
                          hyphenate="false" language="en">
          <fo:static-content flow-name="xsl-region-before">
            <fo:block-container height="25mm" display-align="before">
              <fo:block font-size="10pt" text-align="center" space-after="4mm">
                <xsl:choose>
                  <xsl:when test="//security/@securityClassification='01'">NATO Unclassified</xsl:when>
                  <xsl:otherwise>NATO Unclassified</xsl:otherwise>
                </xsl:choose>
                <xsl:text> • </xsl:text>
                <xsl:text>Applicable to: </xsl:text>
                <xsl:value-of select="//applic/displayText/simplePara"/>
              </fo:block>
              <fo:block border-bottom="1pt solid #000" space-after="8mm"/>
            </fo:block-container>
          </fo:static-content>

          <fo:static-content flow-name="xsl-region-after">
            <fo:block-container height="25mm" display-align="after">
              <fo:block font-size="9pt" line-height="11pt">
                <fo:table table-layout="fixed" width="170mm">
                  <fo:table-column column-width="85mm"/>
                  <fo:table-column column-width="85mm"/>
                  <fo:table-body>
                    <fo:table-row>
                      <fo:table-cell>
                        <fo:block text-align="left" font-family="Helvetica" space-after="2pt">
                          <xsl:text>Applicable to: </xsl:text>
                          <xsl:value-of select="//applic/displayText/simplePara"/>
                        </fo:block>
                        <fo:block text-align="left" font-family="Helvetica" space-after="2pt">
                          <xsl:choose>
                            <xsl:when test="//security/@securityClassification='01'">NATO Unclassified</xsl:when>
                            <xsl:otherwise>NATO Unclassified</xsl:otherwise>
                          </xsl:choose>
                        </fo:block>
                        <fo:block text-align="left" font-family="Helvetica">
                          <xsl:text>End of data module</xsl:text>
                        </fo:block>
                      </fo:table-cell>
                      <fo:table-cell>
                        <fo:block text-align="right" font-family="Helvetica" space-after="2pt">
                          <xsl:value-of select="//dmCode/@modelIdentCode"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@systemDiffCode"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@systemCode"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@subSystemCode"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@subSubSystemCode"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@assyCode"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@disassyCode"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@disassyCodeVariant"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@infoCode"/>
                          <xsl:value-of select="//dmCode/@infoCodeVariant"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="//dmCode/@itemLocationCode"/>
                        </fo:block>
                        <fo:block text-align="right" font-family="Helvetica">
                          <xsl:value-of select="//issueDate/@year"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="format-number(number(//issueDate/@month), '00')"/>
                          <xsl:text>-</xsl:text>
                          <xsl:value-of select="format-number(number(//issueDate/@day), '00')"/>
                          <xsl:text> Page </xsl:text>
                          <fo:page-number/>
                        </fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                  </fo:table-body>
                </fo:table>
              </fo:block>
            </fo:block-container>
          </fo:static-content>

          <fo:flow flow-name="xsl-region-body">
            <fo:block-container width="100%" margin-top="3mm" margin-bottom="3mm">
              <!-- Main Title -->
              <fo:block text-align="center" space-before="40mm" space-after="8mm">
                <fo:block font-family="Helvetica" font-weight="bold" font-size="24pt" line-height="28pt">
                  <xsl:value-of select="//dmTitle/techName"/>
                </fo:block>
                <fo:block font-family="Helvetica" font-style="italic" font-size="14pt" line-height="18pt" space-before="4mm">
                  <xsl:value-of select="//dmTitle/infoName"/>
                </fo:block>
              </fo:block>

              <!-- Table of Contents -->
              <xsl:if test="//description/levelledPara[title]">
                <fo:block space-before="15mm" space-after="8mm">
                  <fo:block font-family="Helvetica" font-weight="bold" font-size="12pt" space-after="6mm">
                    <xsl:text>Table of contents</xsl:text>
                  </fo:block>
                  
                  <fo:table table-layout="fixed" width="170mm" font-size="10pt">
                    <fo:table-column column-width="140mm"/>
                    <fo:table-column column-width="30mm"/>
                    <fo:table-body>
                      <xsl:for-each select="//description/levelledPara[title]">
                        <xsl:variable name="sectionNum" select="count(preceding-sibling::levelledPara[title]) + 1"/>
                        <fo:table-row>
                          <fo:table-cell>
                            <fo:block text-align="left">
                              <xsl:number level="single" count="levelledPara" from="description" format="1"/>
                              <xsl:text> </xsl:text>
                              <xsl:value-of select="title"/>
                              <fo:leader leader-pattern="dots" leader-length.maximum="100%" leader-alignment="reference-area"/>
                            </fo:block>
                          </fo:table-cell>
                          <fo:table-cell>
                            <fo:block text-align="right">
                              <fo:page-number-citation ref-id="section-{$sectionNum}"/>
                            </fo:block>
                          </fo:table-cell>
                        </fo:table-row>
                      </xsl:for-each>
                    </fo:table-body>
                  </fo:table>
                </fo:block>
              </xsl:if>

              <!-- References Section -->
              <fo:block space-before="15mm" space-after="8mm">
                <fo:block font-family="Helvetica" font-weight="bold" font-size="12pt" text-align="center" space-after="4mm">
                  <xsl:text>References</xsl:text>
                </fo:block>
                <fo:block font-family="Helvetica" font-weight="bold" font-size="11pt" text-align="center" space-after="4mm">
                  <xsl:text>Table 1 References</xsl:text>
                </fo:block>
                <fo:table table-layout="fixed" width="170mm" font-size="10pt" border="1pt solid #000">
                  <fo:table-column column-width="85mm"/>
                  <fo:table-column column-width="85mm"/>
                  <fo:table-header>
                    <fo:table-row>
                      <fo:table-cell border="1pt solid #000" padding="2mm">
                        <fo:block font-weight="bold">Data module/Technical publication</fo:block>
                      </fo:table-cell>
                      <fo:table-cell border="1pt solid #000" padding="2mm">
                        <fo:block font-weight="bold">Title</fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                  </fo:table-header>
                  <fo:table-body>
                    <fo:table-row>
                      <fo:table-cell border="1pt solid #000" padding="2mm">
                        <fo:block>None</fo:block>
                      </fo:table-cell>
                      <fo:table-cell border="1pt solid #000" padding="2mm">
                        <fo:block></fo:block>
                      </fo:table-cell>
                    </fo:table-row>
                  </fo:table-body>
                </fo:table>
              </fo:block>
            </fo:block-container>
          </fo:flow>
        </fo:page-sequence>
      </xsl:if>

      <!-- Main Content -->
      <fo:page-sequence master-reference="{$pageMaster}"
                        font-family="Helvetica" font-size="10pt" line-height="12pt"
                        hyphenate="true"
                        language="en">
        <fo:static-content flow-name="xsl-region-before">
          <fo:block-container height="25mm" display-align="before">
            <fo:block font-size="10pt" space-after="4mm" text-align="center" font-family="Helvetica">
              <xsl:choose>
                <xsl:when test="//security/@securityClassification='01'">NATO Unclassified</xsl:when>
                <xsl:otherwise>NATO Unclassified</xsl:otherwise>
              </xsl:choose>
              <xsl:text> </xsl:text>
              <xsl:text>Applicable to: </xsl:text>
              <xsl:value-of select="//applic/displayText/simplePara"/>
            </fo:block>
            <fo:block border-bottom="1pt solid #000" space-after="2mm"/>
          </fo:block-container>
        </fo:static-content>

        <fo:static-content flow-name="xsl-region-after">
          <fo:block-container height="25mm" display-align="after">
            <fo:block font-size="9pt" line-height="11pt">
              <fo:table table-layout="fixed" width="170mm" border-top="1pt solid #000">
                <fo:table-column column-width="60mm"/>
                <fo:table-column column-width="50mm"/>
                <fo:table-column column-width="60mm"/>
                <fo:table-body>
                  <fo:table-row>
                    <fo:table-cell>
                      <fo:block text-align="left" font-family="Helvetica" space-after="8pt">
                        <xsl:text>Applicable to: </xsl:text>
                        <xsl:value-of select="//applic/displayText/simplePara"/>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell>
                      <fo:block text-align="center" font-family="Helvetica" space-after="2pt">
                        <xsl:choose>
                          <xsl:when test="//security/@securityClassification='01'">NATO Unclassified</xsl:when>
                          <xsl:otherwise>NATO Unclassified</xsl:otherwise>
                        </xsl:choose>
                      </fo:block>
                      <fo:block text-align="center" font-family="Helvetica">
                        <xsl:text>End of data module</xsl:text>
                      </fo:block>
                    </fo:table-cell>
                    <fo:table-cell>
                      <fo:block text-align="right" font-family="Helvetica" space-after="2pt">
                        <xsl:value-of select="//dmCode/@modelIdentCode"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@systemDiffCode"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@systemCode"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@subSystemCode"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@subSubSystemCode"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@assyCode"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@disassyCode"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@disassyCodeVariant"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@infoCode"/>
                        <xsl:value-of select="//dmCode/@infoCodeVariant"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="//dmCode/@itemLocationCode"/>
                      </fo:block>
                      <fo:block text-align="right" font-family="Helvetica">
                        <xsl:value-of select="//issueDate/@year"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="format-number(number(//issueDate/@month), '00')"/>
                        <xsl:text>-</xsl:text>
                        <xsl:value-of select="format-number(number(//issueDate/@day), '00')"/>
                        <xsl:text> Page </xsl:text>
                        <fo:page-number/>
                      </fo:block>
                    </fo:table-cell>
                  </fo:table-row>
                </fo:table-body>
              </fo:table>
            </fo:block>
          </fo:block-container>
        </fo:static-content>

        <fo:flow flow-name="xsl-region-body">
          <fo:block-container width="100%" margin-top="4mm" margin-bottom="6mm">
            <!-- description (STYLE description = cor_contentlevel) -->
            <xsl:apply-templates select="//description | //mainProcedure"/>

          <!-- Fallback: if no description/procedure nodes, render headings from params -->
          <xsl:if test="not(//description)">
            <fo:block id="description" space-before="12pt">
              <fo:block font-family="Helvetica" font-weight="bold" font-size="10pt" keep-with-next.within-page="always">
                <xsl:value-of select="$descTextVar"/>
              </fo:block>
            </fo:block>
          </xsl:if>
          <xsl:if test="not(//mainProcedure)">
            <fo:block id="mainProc" space-before="28pt" space-after="28pt">
              <fo:block font-family="Helvetica" font-weight="bold" font-size="10pt" keep-with-next.within-page="always">
                <xsl:value-of select="$procedTextVar"/>
              </fo:block>
            </fo:block>
          </xsl:if>

          <!-- Render procedural steps if any -->
          <xsl:apply-templates select="//proceduralStep"/>
          </fo:block-container>
        </fo:flow>
      </fo:page-sequence>

    </fo:root>
  </xsl:template>

  <!-- cor_idtarget: add id destinations using ${dmDmc}${->id} -->
  <xsl:template match="*[@id]" mode="id-attr">
    <xsl:attribute name="id">
      <xsl:value-of select="concat($dmDmc, @id)"/>
    </xsl:attribute>
  </xsl:template>

  <!-- description -->
  <xsl:template match="description">
    <!-- inherits from cor_contentlevel -->
    <fo:block space-before="0pt" wrap-option="wrap" keep-together.within-page="auto">
      <fo:block id="description" font-family="Helvetica" font-weight="bold" font-size="12pt" 
                keep-with-next.within-page="always" space-after="16pt" wrap-option="wrap"
                text-align="center">
        <xsl:value-of select="$descTextVar"/>
      </fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <!-- mainProcedure -->
  <xsl:template match="mainProcedure">
    <!-- inherits from cor_changeMarkHandling -->
    <fo:block id="mainProc" space-before="28pt" space-after="28pt" wrap-option="wrap">
      <fo:block font-family="Helvetica" font-weight="bold" font-size="10pt" keep-with-next.within-page="always" wrap-option="wrap">
        <xsl:value-of select="$procedTextVar"/>
      </fo:block>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <!-- nestedProceduralStepOrPara and title rendering with numbering -->
  <xsl:template match="proceduralStep">
    <!-- inherits from cor_blockProperties -->
    <fo:block space-after="14pt" wrap-option="wrap">
      <xsl:variable name="level" select="count(ancestor::proceduralStep) + 1"/>
      <fo:block keep-with-next.within-page="always" wrap-option="wrap">
        <xsl:attribute name="font-family">Helvetica</xsl:attribute>
        <xsl:choose>
          <xsl:when test="$level = 1">
            <xsl:attribute name="font-size">14pt</xsl:attribute>
            <xsl:attribute name="line-height">16pt</xsl:attribute>
          </xsl:when>
          <xsl:when test="$level = 2">
            <xsl:attribute name="font-size">12pt</xsl:attribute>
            <xsl:attribute name="line-height">14pt</xsl:attribute>
          </xsl:when>
          <xsl:otherwise>
            <xsl:if test="$level &gt; 4">
              <xsl:attribute name="font-style">oblique</xsl:attribute>
            </xsl:if>
            <xsl:attribute name="font-size">10pt</xsl:attribute>
            <xsl:attribute name="line-height">12pt</xsl:attribute>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:attribute name="id">
          <xsl:text>step-</xsl:text>
          <xsl:number level="multiple" count="proceduralStep" format="1.1.1.1"/>
        </xsl:attribute>
        <xsl:number level="multiple" count="proceduralStep" format="1.1.1.1"/>
        <xsl:text> </xsl:text>
        <xsl:value-of select="normalize-space(title)"/>
      </fo:block>
      <xsl:apply-templates select="node()[not(self::title)]"/>
    </fo:block>
  </xsl:template>

  <!-- levelledPara: section with title and content -->
  <xsl:template match="levelledPara">
    <xsl:variable name="sectionNum" select="count(preceding-sibling::levelledPara[title]) + 1"/>
    <fo:block space-before="14pt" space-after="14pt" wrap-option="wrap" 
              keep-together.within-page="auto" keep-with-next.within-page="auto"
              margin-top="0pt">
      <xsl:if test="title">
        <fo:block font-family="Helvetica" font-weight="bold" font-size="12pt" 
                  keep-with-next.within-page="always" space-after="10pt" 
                  space-before="0pt" wrap-option="wrap" text-indent="0pt"
                  id="section-{$sectionNum}">
          <xsl:if test="$isUpdateHighlighted">
            <xsl:attribute name="margin-left">-20mm</xsl:attribute>
            <xsl:attribute name="padding-left">20mm</xsl:attribute>
            <xsl:attribute name="border-left">2pt solid #000000</xsl:attribute>
            <!-- <xsl:attribute name="background-color">#FFFF99</xsl:attribute> -->
          </xsl:if>
          <xsl:number level="single" count="levelledPara" from="description" format="1"/>
          <xsl:text>  </xsl:text>
          <xsl:apply-templates select="title"/>
        </fo:block>
      </xsl:if>
      <xsl:apply-templates select="node()[not(self::title)]"/>
    </fo:block>
  </xsl:template>

  <!-- title within levelledPara -->
  <xsl:template match="levelledPara/title">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- para: paragraph - handle text and lists separately -->
  <xsl:template match="para">
    <xsl:choose>
      <!-- If para contains randomList, split text and list -->
      <xsl:when test="randomList">
        <!-- Text content before the list - extract text nodes only -->
        <xsl:variable name="textBefore" select="text()[normalize-space()][following-sibling::randomList]"/>
        <xsl:if test="$textBefore or *[not(self::randomList)]">
          <fo:block space-after="10pt" text-align="justify" wrap-option="wrap" 
                    linefeed-treatment="preserve" hyphenate="true" 
                    line-height="12pt" space-before="0pt">
            <xsl:if test="$isUpdateHighlighted">
              <xsl:attribute name="margin-left">-20mm</xsl:attribute>
              <xsl:attribute name="padding-left">20mm</xsl:attribute>
              <xsl:attribute name="border-left">2pt solid #000000</xsl:attribute>
              <!-- <xsl:attribute name="background-color">#FFFF99</xsl:attribute> -->
            </xsl:if>
            <xsl:for-each select="node()[not(self::randomList)]">
              <xsl:choose>
                <xsl:when test="self::text()">
                  <xsl:value-of select="normalize-space(.)"/>
                  <xsl:if test="position() != last()">
                    <xsl:text> </xsl:text>
                  </xsl:if>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:apply-templates select="."/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:for-each>
          </fo:block>
        </xsl:if>
        <!-- List as separate block -->
        <xsl:apply-templates select="randomList"/>
      </xsl:when>
      <!-- Normal para without lists -->
      <xsl:otherwise>
        <fo:block space-after="8pt" space-before="0pt" text-align="justify" wrap-option="wrap" 
                  linefeed-treatment="preserve" hyphenate="true" line-height="12pt">
          <xsl:if test="$isUpdateHighlighted">
            <xsl:attribute name="margin-left">-20mm</xsl:attribute>
            <xsl:attribute name="padding-left">20mm</xsl:attribute>
            <xsl:attribute name="border-left">2pt solid #000000</xsl:attribute>
            <!-- <xsl:attribute name="background-color">#FFFF99</xsl:attribute> -->
          </xsl:if>
          <xsl:apply-templates/>
        </fo:block>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- simplePara: simple paragraph -->
  <xsl:template match="simplePara">
    <fo:block space-after="6pt" space-before="0pt" text-align="justify" wrap-option="wrap" 
              linefeed-treatment="preserve" hyphenate="true" line-height="12pt">
      <xsl:if test="$isUpdateHighlighted">
        <xsl:attribute name="margin-left">-20mm</xsl:attribute>
        <xsl:attribute name="padding-left">20mm</xsl:attribute>
        <xsl:attribute name="border-left">2pt solid #000000</xsl:attribute>
        <!-- <xsl:attribute name="background-color">#FFFF99</xsl:attribute> -->
      </xsl:if>
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <!-- randomList: unordered list -->
  <xsl:template match="randomList">
    <xsl:variable name="parentSection" select="ancestor::levelledPara[1]"/>
    <xsl:variable name="sectionNum" select="count($parentSection/preceding-sibling::levelledPara[title]) + 1"/>
    <xsl:choose>
      <!-- For sections 4 and 5, use simple block container with aligned hyphens -->
      <xsl:when test="$sectionNum = 4 or $sectionNum = 5">
        <fo:block space-after="10pt" space-before="6pt" text-indent="0pt">
          <xsl:apply-templates select="listItem"/>
        </fo:block>
      </xsl:when>
      <!-- For other sections, use standard list-block with aligned bullets -->
      <xsl:otherwise>
        <fo:list-block space-after="10pt" space-before="6pt" 
                       provisional-distance-between-starts="4mm" 
                       provisional-label-separation="2mm">
          <xsl:apply-templates select="listItem"/>
        </fo:list-block>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- listItem: list item - use hyphen for sections 4 and 5, bullet for others -->
  <xsl:template match="listItem">
    <xsl:variable name="parentSection" select="ancestor::levelledPara[1]"/>
    <xsl:variable name="sectionNum" select="count($parentSection/preceding-sibling::levelledPara[title]) + 1"/>
    <xsl:choose>
      <!-- For sections 4 and 5, use hyphen with consistent indentation -->
      <xsl:when test="$sectionNum = 4 or $sectionNum = 5">
        <fo:block>
          <xsl:if test="$isUpdateHighlighted">
            <xsl:attribute name="margin-left">-20mm</xsl:attribute>
            <xsl:attribute name="padding-left">20mm</xsl:attribute>
            <xsl:attribute name="border-left">2pt solid #000000</xsl:attribute>
            <!-- <xsl:attribute name="background-color">#FFFF99</xsl:attribute> -->
          </xsl:if>
          <fo:block wrap-option="wrap" linefeed-treatment="preserve" text-align="justify" 
                    hyphenate="true" space-after="6pt" space-before="0pt"
                    line-height="12pt" text-indent="0pt" margin-left="4mm">
            <fo:inline>- </fo:inline>
            <xsl:apply-templates/>
          </fo:block>
        </fo:block>
      </xsl:when>
      <!-- For other sections, use standard list with bullet -->
      <xsl:otherwise>
        <fo:list-item>
          <fo:list-item-label end-indent="label-end()">
            <fo:block>•</fo:block>
          </fo:list-item-label>
          <fo:list-item-body start-indent="body-start()">
            <fo:block wrap-option="wrap" linefeed-treatment="preserve" text-align="justify" 
                      hyphenate="true" space-after="6pt" space-before="0pt"
                      line-height="12pt" text-indent="0pt" margin-left="0pt">
              <xsl:if test="$isUpdateHighlighted">
                <xsl:attribute name="margin-left">-20mm</xsl:attribute>
                <xsl:attribute name="padding-left">20mm</xsl:attribute>
                <xsl:attribute name="border-left">2pt solid #000000</xsl:attribute>
                <!-- <xsl:attribute name="background-color">#FFFF99</xsl:attribute> -->
              </xsl:if>
              <xsl:apply-templates/>
            </fo:block>
          </fo:list-item-body>
        </fo:list-item>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- emphasis: bold text -->
  <xsl:template match="emphasis">
    <fo:inline font-weight="bold">
      <xsl:apply-templates/>
    </fo:inline>
  </xsl:template>

  <!-- para within listItem - output text inline without creating additional blocks -->
  <xsl:template match="listItem/para">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- copyrightPara -->
  <xsl:template match="copyrightPara">
    <fo:block space-after="6pt" text-align="justify" wrap-option="wrap" linefeed-treatment="preserve" hyphenate="true">
      <xsl:apply-templates/>
    </fo:block>
  </xsl:template>

  <!-- Generic text nodes - preserve whitespace but allow wrapping -->
  <xsl:template match="text()">
    <xsl:value-of select="."/>
  </xsl:template>

  <!-- Default: ignore unknown elements but process children -->
  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>