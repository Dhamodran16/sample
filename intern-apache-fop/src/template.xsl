<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version="1.0">

    <xsl:variable name="docTitle">
        <xsl:choose>
            <xsl:when test="/book"><xsl:value-of select="/book/@title"/></xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/dmodule/identAndStatusSection/dmAddress/dmAddressItems/dmTitle/techName"/>
                <xsl:text> - </xsl:text>
                <xsl:value-of select="/dmodule/identAndStatusSection/dmAddress/dmAddressItems/dmTitle/infoName"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="docCode">
        <xsl:choose>
            <xsl:when test="/book"><xsl:value-of select="/book/@id"/></xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(
                    /dmodule/identAndStatusSection/dmAddress/dmIdent/dmCode/@modelIdentCode, '-', 
                    /dmodule/identAndStatusSection/dmAddress/dmIdent/dmCode/@systemCode, '-', 
                    /dmodule/identAndStatusSection/dmAddress/dmIdent/dmCode/@infoCode
                )"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="docDate">
        <xsl:choose>
            <xsl:when test="/book/metadata/date"><xsl:value-of select="/book/metadata/date"/></xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat(
                    /dmodule/identAndStatusSection/dmAddress/dmAddressItems/issueDate/@year, '-', 
                    /dmodule/identAndStatusSection/dmAddress/dmAddressItems/issueDate/@month, '-', 
                    /dmodule/identAndStatusSection/dmAddress/dmAddressItems/issueDate/@day
                )"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>

    <xsl:variable name="securityLevel">
        <xsl:choose>
            <xsl:when test="/book/metadata/author">Author: <xsl:value-of select="/book/metadata/author"/></xsl:when>
            <xsl:when test="//security/@securityClassification = '01'">UNCLASSIFIED</xsl:when>
            <xsl:when test="//security/@securityClassification = '02'">RESTRICTED</xsl:when>
            <xsl:otherwise>OFFICIAL</xsl:otherwise>
        </xsl:choose>
    </xsl:variable>


    <xsl:template name="start-change-mark">
        <xsl:if test="(@updateHighlight and @updateHighlight!='0') or 
                      (@changeMark and @changeMark!='0') or 
                      contains(@changeType, 'modified') or
                      contains(@issueType, 'change') or contains(@issueType, 'new')">
            <fo:change-bar-begin change-bar-class="{generate-id()}" 
                                 change-bar-style="solid" change-bar-width="1pt" 
                                 change-bar-offset="5mm" color="#AAAAAA"/>
        </xsl:if>
    </xsl:template>

    <xsl:template name="end-change-mark">
        <xsl:if test="(@updateHighlight and @updateHighlight!='0') or 
                      (@changeMark and @changeMark!='0') or 
                      contains(@changeType, 'modified') or
                      contains(@issueType, 'change') or contains(@issueType, 'new')">
            <fo:change-bar-end change-bar-class="{generate-id()}"/>
        </xsl:if>
    </xsl:template>


    <xsl:template match="/">
        <fo:root font-family="Helvetica, Arial, sans-serif" font-size="10pt">
            <fo:layout-master-set>
                <fo:simple-page-master master-name="A4" page-width="210mm" page-height="297mm"
                                       margin-top="15mm" margin-bottom="15mm" margin-left="25mm" margin-right="15mm">
                    <fo:region-body margin-top="20mm" margin-bottom="20mm"/>
                    <fo:region-before extent="15mm"/>
                    <fo:region-after extent="15mm"/>
                </fo:simple-page-master>
            </fo:layout-master-set>

            <fo:page-sequence master-reference="A4">
                
                <fo:static-content flow-name="xsl-region-before">
                    <fo:block text-align="center" border-bottom="0.5pt solid #000" padding-bottom="2pt" font-weight="bold" font-size="9pt">
                        <xsl:value-of select="$securityLevel"/>
                    </fo:block>
                </fo:static-content>

                <fo:static-content flow-name="xsl-region-after">
                    <fo:block border-top="0.5pt solid #000" padding-top="2pt" font-size="9pt">
                        <fo:table table-layout="fixed" width="100%">
                            <fo:table-column column-width="40%"/>
                            <fo:table-column column-width="20%"/>
                            <fo:table-column column-width="40%"/>
                            <fo:table-body>
                                <fo:table-row>
                                    <fo:table-cell><fo:block><xsl:value-of select="$docCode"/></fo:block></fo:table-cell>
                                    <fo:table-cell><fo:block text-align="center">Page <fo:page-number/></fo:block></fo:table-cell>
                                    <fo:table-cell>
                                        <fo:block text-align="right">
                                            <xsl:value-of select="$docDate"/>
                                        </fo:block>
                                    </fo:table-cell>
                                </fo:table-row>
                            </fo:table-body>
                        </fo:table>
                    </fo:block>
                </fo:static-content>

                <fo:flow flow-name="xsl-region-body">
                    <fo:block font-size="24pt" font-weight="bold" space-after="20mm" text-align="center" color="#333">
                        <xsl:value-of select="$docTitle"/>
                    </fo:block>

                    <xsl:choose>
                        <xsl:when test="/book">
                            <xsl:apply-templates select="/book/chapter"/>
                        </xsl:when>
                        
                        <xsl:when test="//illustratedPartsCatalog">
                            <xsl:apply-templates select="//illustratedPartsCatalog"/>
                        </xsl:when>
                        
                        <xsl:when test="//procedure">
                            <xsl:apply-templates select="//procedure"/>
                        </xsl:when>
                        
                        <xsl:otherwise>
                            <xsl:apply-templates select="//content"/>
                        </xsl:otherwise>
                    </xsl:choose>
                    
                    <fo:block space-before="20mm" text-align="center" font-style="italic" color="#AAA" font-size="9pt">
                        *** End of Document ***
                    </fo:block>
                </fo:flow>
            </fo:page-sequence>
        </fo:root>
    </xsl:template>


    <xsl:template match="internalRef">
        <fo:basic-link internal-destination="{@internalRefId}" color="blue" text-decoration="underline">
            <xsl:text>[Ref: </xsl:text>
            <xsl:value-of select="@internalRefId"/>
            <xsl:text>]</xsl:text>
        </fo:basic-link>
    </xsl:template>

    <xsl:template match="refs">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-weight="bold" space-after="6pt" border-bottom="1pt solid #DDD">References:</fo:block>
        <fo:list-block space-after="12pt">
            <xsl:apply-templates/>
        </fo:list-block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="refs/dmRef">
        <xsl:call-template name="start-change-mark"/>
        <fo:list-item>
            <fo:list-item-label end-indent="label-end()"><fo:block>•</fo:block></fo:list-item-label>
            <fo:list-item-body start-indent="body-start()">
                <fo:block font-family="monospace" font-size="9pt">
                    <xsl:value-of select="concat(dmRefIdent/dmCode/@modelIdentCode, '-', dmRefIdent/dmCode/@systemCode, '-', dmRefIdent/dmCode/@infoCode)"/>
                </fo:block>
            </fo:list-item-body>
        </fo:list-item>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="figure">
        <xsl:call-template name="start-change-mark"/>
        <fo:block id="{@id}" font-weight="bold" space-after="10pt" text-align="center" border="1pt solid #DDD" padding="10pt" keep-together.within-page="always">
            [FIGURE: <xsl:value-of select="title"/>]
            <xsl:apply-templates select="graphic"/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="graphic">
        <fo:block font-size="8pt" font-weight="normal" color="#666" space-before="5pt">
            [Image Source: <xsl:value-of select="@infoEntityIdent"/>]
        </fo:block>
        <xsl:if test="hotspot">
            <fo:block font-size="8pt" text-align="left" margin-top="5pt" border-top="1pt dashed #EEE" padding-top="2pt">
                <fo:inline font-weight="bold">Hotspots:</fo:inline>
                <xsl:apply-templates select="hotspot"/>
            </fo:block>
        </xsl:if>
    </xsl:template>

    <xsl:template match="hotspot">
        <fo:block id="{@id}" margin-left="5pt">
            • <xsl:value-of select="@hotspotTitle"/> (ID: <xsl:value-of select="@applicationStructureIdent"/>)
        </fo:block>
    </xsl:template>

    <xsl:template match="definitionList">
        <xsl:call-template name="start-change-mark"/>
        <fo:block space-after="12pt">
            <xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="definitionListItem">
        <xsl:call-template name="start-change-mark"/>
        <fo:block space-after="8pt" keep-together.within-page="always">
            <xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="listItemTerm">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-weight="bold" color="#333" space-after="2pt">
            <xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="listItemDefinition">
        <xsl:call-template name="start-change-mark"/>
        <fo:block start-indent="8mm" border-left="2pt solid #EEE" padding-left="4mm">
            <xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="para/dmRef | listItemDefinition/dmRef">
        <fo:inline font-family="monospace" font-size="9pt" color="#000088">
            [Ref: <xsl:value-of select=".//dmCode/@infoCode"/>]
        </fo:inline>
    </xsl:template>

    <xsl:template match="chapter">
        <xsl:call-template name="start-change-mark"/>
        <fo:block break-before="page" space-after="10pt">
            <fo:block font-size="18pt" font-weight="bold" border-bottom="2pt solid black" space-after="10pt" padding-bottom="4pt">
                <xsl:value-of select="@title"/>
            </fo:block>
            <xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="section">
        <xsl:call-template name="start-change-mark"/>
        <fo:block space-before="15pt" space-after="10pt">
            <fo:block font-size="14pt" font-weight="bold" color="#444">
                <xsl:value-of select="@title"/>
            </fo:block>
            <xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>
    
    <xsl:template match="subject">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-size="12pt" font-weight="bold" space-before="10pt" space-after="6pt" color="#555" border-bottom="1pt solid #EEE">
            <xsl:value-of select="@name"/>
        </fo:block>
        <xsl:apply-templates/>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="pageblock">
        <xsl:call-template name="start-change-mark"/>
        <fo:block space-after="10pt"><xsl:apply-templates/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="heading">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-size="11pt" font-weight="bold" space-after="4pt" color="#666"><xsl:apply-templates/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="task">
        <xsl:call-template name="start-change-mark"/>
        <fo:block border="1pt solid #EEE" padding="10pt" space-after="10pt">
            <fo:block font-weight="bold" space-after="5pt">Task: <xsl:value-of select="@name"/></fo:block>
            <xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="step">
        <xsl:call-template name="start-change-mark"/>
        <fo:list-block provisional-distance-between-starts="10mm" space-after="6pt">
            <fo:list-item>
                <fo:list-item-label end-indent="label-end()"><fo:block font-weight="bold"><xsl:value-of select="@number"/>.</fo:block></fo:list-item-label>
                <fo:list-item-body start-indent="body-start()"><fo:block><xsl:apply-templates/></fo:block></fo:list-item-body>
            </fo:list-item>
        </fo:list-block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>
    
    <xsl:template match="tools">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-weight="bold" space-before="8pt" space-after="2pt" color="#333">Tools Required:</fo:block>
        <fo:list-block provisional-distance-between-starts="5mm"><xsl:apply-templates/></fo:list-block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="safetyWarnings">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-weight="bold" space-before="10pt" space-after="4pt" color="red">⚠ SAFETY WARNINGS:</fo:block>
        <xsl:apply-templates/>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="warning">
        <xsl:call-template name="start-change-mark"/>
        <fo:block border="1pt solid red" padding="4pt" margin="4pt" background-color="#FFEEEE" font-weight="bold" color="red">WARNING: <xsl:apply-templates/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="caution">
        <xsl:call-template name="start-change-mark"/>
        <fo:block border="1pt solid orange" padding="4pt" margin="4pt" background-color="#FFFFEE" font-weight="bold" color="#CC8800">CAUTION: <xsl:apply-templates/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="note">
        <xsl:call-template name="start-change-mark"/>
        <fo:block border="1pt solid #999" padding="4pt" margin="4pt" background-color="#EEEEEE" font-style="italic">NOTE: <xsl:apply-templates/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="estimatedTime">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-style="italic" space-before="6pt" color="#666" border-top="1pt dashed #CCC" padding-top="4pt">
            <fo:inline font-weight="bold">Estimated Time: </fo:inline>
            <xsl:apply-templates/><xsl:text> </xsl:text><xsl:value-of select="@unit"/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>
    
    <xsl:template match="expectedResult">
         <xsl:call-template name="start-change-mark"/>
         <fo:block font-style="italic" color="green" space-after="4pt">Result: <xsl:apply-templates/></fo:block>
         <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="metadata">
         <fo:block font-size="9pt" color="#888" space-after="20pt" text-align="center">
            <xsl:if test="publisher">Publisher: <xsl:value-of select="publisher"/> | </xsl:if>
            <xsl:if test="isbn">ISBN: <xsl:value-of select="isbn"/></xsl:if>
        </fo:block>
    </xsl:template>

    <xsl:template match="illustratedPartsCatalog">
        <xsl:apply-templates select="figure"/>
        <xsl:apply-templates select="partsList"/>
    </xsl:template>

    <xsl:template match="partsList">
        <fo:table width="100%" table-layout="fixed" border-collapse="collapse">
            <fo:table-column column-width="10%"/>
            <fo:table-column column-width="20%"/>
            <fo:table-column column-width="50%"/>
            <fo:table-column column-width="10%"/>
            <fo:table-column column-width="10%"/>
            <fo:table-header>
                <fo:table-row background-color="#EEE" font-weight="bold">
                    <fo:table-cell border="1pt solid black" padding="2pt"><fo:block>Lvl</fo:block></fo:table-cell>
                    <fo:table-cell border="1pt solid black" padding="2pt"><fo:block>Part No</fo:block></fo:table-cell>
                    <fo:table-cell border="1pt solid black" padding="2pt"><fo:block>Description</fo:block></fo:table-cell>
                    <fo:table-cell border="1pt solid black" padding="2pt"><fo:block>Qty</fo:block></fo:table-cell>
                    <fo:table-cell border="1pt solid black" padding="2pt"><fo:block>CAGE</fo:block></fo:table-cell>
                </fo:table-row>
            </fo:table-header>
            <fo:table-body><xsl:apply-templates select="partTreeNode"/></fo:table-body>
        </fo:table>
    </xsl:template>

    <xsl:template match="partTreeNode">
        <xsl:call-template name="start-change-mark"/>
        <fo:table-row>
            <fo:table-cell border="0.5pt solid black" padding="2pt"><fo:block text-align="center"><xsl:value-of select="@indenture"/></fo:block></fo:table-cell>
            <fo:table-cell border="0.5pt solid black" padding="2pt"><fo:block font-family="monospace"><xsl:value-of select="itemIdentData/partNumber"/></fo:block></fo:table-cell>
            <fo:table-cell border="0.5pt solid black" padding="2pt">
                <fo:block><xsl:attribute name="start-indent"><xsl:value-of select="concat((@indenture - 1) * 4, 'mm')"/></xsl:attribute><xsl:value-of select="itemIdentData/descrForPart"/></fo:block>
            </fo:table-cell>
            <fo:table-cell border="0.5pt solid black" padding="2pt"><fo:block text-align="center"><xsl:value-of select="itemIdentData/quantityPerNextHigherAssy"/></fo:block></fo:table-cell>
            <fo:table-cell border="0.5pt solid black" padding="2pt"><fo:block text-align="center"><xsl:value-of select="itemIdentData/nscm"/></fo:block></fo:table-cell>
        </fo:table-row>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="procedure">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="preliminaryRqmts">
        <fo:block font-weight="bold" space-after="6pt" border-bottom="1pt solid black">Requirements:</fo:block>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="supportEquipDescr | supplyDescr | spareDescr | tool">
        <xsl:call-template name="start-change-mark"/>
        <fo:block start-indent="5mm" space-after="2pt">• <xsl:value-of select="."/><xsl:value-of select="name"/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="proceduralStep">
        <xsl:call-template name="start-change-mark"/>
        <fo:block space-before="6pt" space-after="6pt">
            <xsl:if test="title"><fo:block font-weight="bold" space-after="2pt"><xsl:value-of select="title"/></fo:block></xsl:if>
            <fo:block margin-left="4mm"><xsl:apply-templates select="*[not(self::title)]"/></fo:block>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="description">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="para | simplePara | p | intro/para">
        <xsl:call-template name="start-change-mark"/>
        <fo:block space-after="8pt" text-align="justify" line-height="1.4"><xsl:apply-templates/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="levelledPara">
        <fo:block space-after="12pt"><xsl:apply-templates/></fo:block>
    </xsl:template>

    <xsl:template match="levelledPara/title">
        <xsl:call-template name="start-change-mark"/>
        <fo:block font-weight="bold" keep-with-next="always" space-after="6pt" space-before="12pt" font-size="12pt">
            <xsl:number level="multiple" format="1.1 " count="levelledPara"/><xsl:text>  </xsl:text><xsl:apply-templates/>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="randomList | list | ul | ol">
        <xsl:call-template name="start-change-mark"/>
        <fo:list-block provisional-distance-between-starts="6mm" space-after="8pt" margin-left="5mm"><xsl:apply-templates select="listItem | li"/></fo:list-block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="listItem | li">
        <xsl:call-template name="start-change-mark"/>
        <fo:list-item space-after="4pt">
            <fo:list-item-label end-indent="label-end()"><fo:block>•</fo:block></fo:list-item-label>
            <fo:list-item-body start-indent="body-start()"><fo:block><xsl:apply-templates/></fo:block></fo:list-item-body>
        </fo:list-item>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="table">
        <xsl:call-template name="start-change-mark"/>
        <fo:block space-before="10pt" space-after="10pt">
            <fo:table width="100%" table-layout="fixed" border-collapse="separate" border="0.5pt solid black">
                <xsl:apply-templates select=".//tgroup"/>
            </fo:table>
        </fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="tgroup">
        <fo:table-body>
            <xsl:apply-templates select=".//row | .//tr"/>
        </fo:table-body>
    </xsl:template>

    <xsl:template match="row | tr">
        <fo:table-row>
            <xsl:apply-templates select="entry | td"/>
        </fo:table-row>
    </xsl:template>

    <xsl:template match="entry | td">
        <fo:table-cell border="0.5pt solid black" padding="4pt">
            <fo:block>
                <xsl:apply-templates/>
            </fo:block>
        </fo:table-cell>
    </xsl:template>
    
    <xsl:template match="reqCond">
        <xsl:call-template name="start-change-mark"/>
        <fo:block margin-left="5mm" space-after="2pt">• <xsl:value-of select="noCond"/></fo:block>
        <xsl:call-template name="end-change-mark"/>
    </xsl:template>

    <xsl:template match="emphasis | bold | b">
        <fo:inline font-weight="bold"><xsl:apply-templates/></fo:inline>
    </xsl:template>
    <xsl:template match="italic | i">
        <fo:inline font-style="italic"><xsl:apply-templates/></fo:inline>
    </xsl:template>
    <xsl:template match="underline | u">
        <fo:inline text-decoration="underline"><xsl:apply-templates/></fo:inline>
    </xsl:template>

    <xsl:template match="*">
        <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
