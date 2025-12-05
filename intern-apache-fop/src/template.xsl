<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version="1.0">

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
    <xsl:param name="pageMaster" select="'simpleA4'"/>

    <xsl:variable name="isUpdateHighlighted" select="boolean(//reasonForUpdate[@updateHighlight='1'])"/>
    <xsl:variable name="updateHighlightId" select="//reasonForUpdate[@updateHighlight='1']/@id"/>

    <xsl:template match="/">
        <fo:root font-family="Abadi, sans-serif" font-weight="normal" font-size="10pt">
            <fo:layout-master-set>
                <fo:simple-page-master master-name="simpleA4"
                                       page-width="210mm" page-height="297mm"
                                       margin-top="10mm" margin-bottom="10mm"
                                       margin-left="20mm" margin-right="15mm">
                    
                    <fo:region-body margin-top="22mm" margin-bottom="30mm"/>
                    
                    <fo:region-before extent="20mm"/>
                    
                    <fo:region-after extent="25mm"/>
                </fo:simple-page-master>
            </fo:layout-master-set>

            <fo:bookmark-tree>
                <xsl:if test="//description">
                    <fo:bookmark internal-destination="description">
                        <fo:bookmark-title><xsl:value-of select="$descTextVar"/></fo:bookmark-title>
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

            <fo:page-sequence master-reference="simpleA4" initial-page-number="1" language="en">
                
                <fo:static-content flow-name="xsl-region-before">
                    <fo:block font-size="10pt">
                        <fo:block text-align="center" space-after="2mm">
                            <xsl:choose>
                                <xsl:when test="//security/@securityClassification='01'">NATO Unclassified</xsl:when>
                                <xsl:otherwise>NATO Unclassified</xsl:otherwise>
                            </xsl:choose>
                            <xsl:text> &#x2022; </xsl:text>
                            <xsl:text>Applicable to: </xsl:text>
                            <xsl:value-of select="//applic/displayText/simplePara"/>
                        </fo:block>
                        <fo:block border-bottom="0.5pt solid #000"/>
                    </fo:block>
                </fo:static-content>

                <fo:static-content flow-name="xsl-region-after">
                    <fo:block font-size="9pt">
                        <fo:block border-top="0.5pt solid #000" space-after="2mm"/>
                        
                        <fo:table table-layout="fixed" width="100%">
                            <fo:table-column column-width="30%"/>
                            <fo:table-column column-width="20%"/>
                            <fo:table-column column-width="50%"/>
                            <fo:table-body>
                                <fo:table-row>
                                    <fo:table-cell>
                                        <fo:block text-align="left">
                                            <xsl:text>Applicable to: </xsl:text>
                                            <xsl:value-of select="//applic/displayText/simplePara"/>
                                        </fo:block>
                                    </fo:table-cell>
                                    
                                    <fo:table-cell>
                                        <fo:block text-align="center" font-weight="bold">
                                            <xsl:choose>
                                                <xsl:when test="//security/@securityClassification='01'">NATO Unclassified</xsl:when>
                                                <xsl:otherwise>NATO Unclassified</xsl:otherwise>
                                            </xsl:choose>
                                        </fo:block>
                                        <fo:block text-align="center" font-style="italic" font-weight="normal">
                                            <xsl:text>End of data module</xsl:text>
                                        </fo:block>
                                    </fo:table-cell>
                                    
                                    <fo:table-cell>
                                        <fo:block text-align="right" font-weight="bold" wrap-option="no-wrap">
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
                                        <fo:block text-align="right" font-weight="normal">
                                            <xsl:value-of select="concat(//issueDate/@year, '-', format-number(//issueDate/@month, '00'), '-', format-number(//issueDate/@day, '00'))"/>
                                            <xsl:text> Page </xsl:text>
                                            <fo:page-number/>
                                        </fo:block>
                                    </fo:table-cell>
                                </fo:table-row>
                            </fo:table-body>
                        </fo:table>
                    </fo:block>
                </fo:static-content>

                <fo:flow flow-name="xsl-region-body">
                    <fo:block text-align="center" space-after="4mm">
                        <fo:block font-weight="bold" font-size="18pt">
                            <xsl:value-of select="//dmTitle/techName"/>
                        </fo:block>
                        <fo:block font-style="italic" font-size="12pt" font-weight="normal">
                            <xsl:value-of select="//dmTitle/infoName"/>
                        </fo:block>
                    </fo:block>

                    <xsl:if test="//description/levelledPara[title]">
                        <fo:block space-after="6mm">
                            <fo:block font-weight="bold" font-size="12pt" space-after="3mm">
                                <xsl:text>Table of contents</xsl:text>
                            </fo:block>
                            <fo:table table-layout="fixed" width="100%" font-size="10pt">
                                <fo:table-column column-width="90%"/>
                                <fo:table-column column-width="10%"/>
                                <fo:table-body>
                                    <xsl:for-each select="//description/levelledPara[title]">
                                        <xsl:variable name="sectionNum" select="count(preceding-sibling::levelledPara[title]) + 1"/>
                                        <fo:table-row>
                                            <fo:table-cell>
                                                <fo:block text-align="left" text-align-last="justify" font-weight="normal">
                                                    <xsl:number level="single" count="levelledPara" from="description" format="1"/>
                                                    <xsl:text> </xsl:text>
                                                    <xsl:value-of select="title"/>
                                                    <fo:leader leader-pattern="dots"/>
                                                </fo:block>
                                            </fo:table-cell>
                                            <fo:table-cell>
                                                <fo:block text-align="right" font-weight="normal">
                                                    <fo:page-number-citation ref-id="section-{$sectionNum}"/>
                                                </fo:block>
                                            </fo:table-cell>
                                        </fo:table-row>
                                    </xsl:for-each>
                                </fo:table-body>
                            </fo:table>
                        </fo:block>
                    </xsl:if>

                    <fo:block space-after="6mm">
                        <fo:block font-weight="bold" font-size="12pt" text-align="center" space-after="2mm">
                            <xsl:text>References</xsl:text>
                        </fo:block>
                        <fo:block font-weight="normal" font-size="11pt" text-align="center" space-after="2mm">
                            <xsl:text>Table 1 References</xsl:text>
                        </fo:block>
                        
                        <fo:block border-top="0.5pt solid black" border-bottom="0.5pt solid black" padding-top="2pt" padding-bottom="2pt">
                            <fo:block text-align-last="justify" font-weight="bold" font-size="10pt">
                                <fo:inline>Data module/Technical publication</fo:inline>
                                <fo:leader leader-pattern="space"/>
                                <fo:inline>Title</fo:inline>
                            </fo:block>
                        </fo:block>
                        <fo:block border-bottom="0.5pt solid black" padding-top="2pt" padding-bottom="2pt">
                            <fo:block text-align-last="justify" font-size="10pt" font-weight="normal">
                                <fo:inline>None</fo:inline>
                                <fo:leader leader-pattern="space"/>
                                <fo:inline></fo:inline>
                            </fo:block>
                        </fo:block>
                    </fo:block>

                    <xsl:apply-templates select="//description | //mainProcedure"/>
                    <xsl:apply-templates select="//proceduralStep"/>

                    <xsl:if test="//restrictionInfo/copyright">
                        <fo:block space-before="10mm" font-size="9pt" border-top="0.5pt solid black" padding-top="4pt">
                            <fo:block font-weight="bold" space-after="2mm">Copyright &amp; Legal:</fo:block>
                            <xsl:apply-templates select="//restrictionInfo/copyright"/>
                        </fo:block>
                    </xsl:if>
                </fo:flow>
            </fo:page-sequence>
        </fo:root>
    </xsl:template>

    <xsl:template match="*[@id]" mode="id-attr">
        <xsl:attribute name="id">
            <xsl:value-of select="concat($dmDmc, @id)"/>
        </xsl:attribute>
    </xsl:template>

    <xsl:template match="description">
        <fo:block id="description" font-weight="bold" font-size="12pt" 
                  space-before="0pt" space-after="6pt" text-align="center">
            <xsl:value-of select="$descTextVar"/>
        </fo:block>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="mainProcedure">
        <fo:block id="mainProc" space-before="12pt" space-after="12pt">
            <fo:block font-weight="bold" font-size="10pt" keep-with-next.within-page="always">
                <xsl:value-of select="$procedTextVar"/>
            </fo:block>
            <xsl:apply-templates/>
        </fo:block>
    </xsl:template>

    <xsl:template match="levelledPara">
        <xsl:variable name="sectionNum" select="count(preceding-sibling::levelledPara[title]) + 1"/>
        <fo:block space-before="10pt" space-after="10pt" id="section-{$sectionNum}">
            <xsl:if test="title">
                <fo:block font-weight="bold" font-size="11pt" 
                          keep-with-next.within-page="always" space-after="4pt">
                    <xsl:if test="$isUpdateHighlighted">
                        <xsl:attribute name="border-left">0.5pt solid #000000</xsl:attribute>
                        <xsl:attribute name="padding-left">2mm</xsl:attribute>
                        <xsl:attribute name="margin-left">-2mm</xsl:attribute>
                    </xsl:if>
                    <xsl:number level="single" count="levelledPara" from="description" format="1"/>
                    <xsl:text>.&#160;&#160;&#160;</xsl:text>
                    <xsl:apply-templates select="title"/>
                </fo:block>
            </xsl:if>
            <xsl:apply-templates select="node()[not(self::title)]"/>
        </fo:block>
    </xsl:template>

    <xsl:template match="levelledPara/title">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="para">
        <fo:block text-align="justify" space-after="6pt" line-height="1.2" font-weight="normal">
            <xsl:if test="$isUpdateHighlighted and not(parent::listItem)">
                <xsl:attribute name="border-left">0.5pt solid #000000</xsl:attribute>
                <xsl:attribute name="padding-left">2mm</xsl:attribute>
                <xsl:attribute name="margin-left">-2mm</xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </fo:block>
    </xsl:template>

    <xsl:template match="simplePara">
        <fo:block space-after="6pt" text-align="justify" line-height="1.2" font-weight="normal">
            <xsl:if test="$isUpdateHighlighted and not(parent::listItem)">
                <xsl:attribute name="border-left">0.5pt solid #000000</xsl:attribute>
                <xsl:attribute name="padding-left">2mm</xsl:attribute>
                <xsl:attribute name="margin-left">-2mm</xsl:attribute>
            </xsl:if>
            <xsl:apply-templates/>
        </fo:block>
    </xsl:template>

    <xsl:template match="randomList">
        <fo:list-block space-after="6pt" space-before="6pt" 
                       provisional-distance-between-starts="8mm" 
                       provisional-label-separation="2mm">
            <xsl:apply-templates select="listItem"/>
        </fo:list-block>
    </xsl:template>

    <xsl:template match="listItem">
        <xsl:variable name="isHyphenated" select="parent::randomList/@listItemPrefix = 'pf02'"/>
        <fo:list-item>
            <xsl:if test="$isUpdateHighlighted and not($isHyphenated)">
                <xsl:attribute name="border-left">0.5pt solid #000000</xsl:attribute>
                <xsl:attribute name="padding-left">2mm</xsl:attribute>
                <xsl:attribute name="margin-left">-2mm</xsl:attribute>
            </xsl:if>

            <fo:list-item-label end-indent="label-end()">
                <fo:block font-weight="normal">
                    <xsl:choose>
                        <xsl:when test="$isHyphenated">
                            <xsl:text>-</xsl:text>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>&#x2022;</xsl:text>
                        </xsl:otherwise>
                    </xsl:choose>
                </fo:block>
            </fo:list-item-label>
            <fo:list-item-body start-indent="body-start()">
                <fo:block font-weight="normal">
                    <xsl:apply-templates/>
                </fo:block>
            </fo:list-item-body>
        </fo:list-item>
    </xsl:template>

    <xsl:template match="emphasis">
        <fo:inline font-weight="bold"><xsl:apply-templates/></fo:inline>
    </xsl:template>

    <xsl:template match="listItem/para">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="copyrightPara">
        <fo:block space-after="6pt" font-weight="normal"><xsl:apply-templates/></fo:block>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:value-of select="."/>
    </xsl:template>

    <xsl:template match="*">
        <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
