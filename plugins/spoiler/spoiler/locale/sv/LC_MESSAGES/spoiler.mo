��          L      |       �   �  �      C     L     f  $   m  �  �  �  `  
   "     -  	   I  $   S                                         Add command (:spoiler:) in wiki parser.

<B>Usage:</B>
<PRE>(:spoiler:)
Text
(:spoilerend:)</PRE>

For nested spoilers use (:spoiler0:), (:spoiler1:)... (:spoiler9:) commands. 

<U>Example:</U>

<PRE>(:spoiler:)
Text
&nbsp;&nbsp;&nbsp;(:spoiler1:)
&nbsp;&nbsp;&nbsp;Nested spoiler
&nbsp;&nbsp;&nbsp;(:spoiler1end:)
(:spoilerend:)</PRE>

<B>Params:</B>
<U>inline</U> - Spoiler will be in inline mode.
<U>expandtext</U> - Link text for the collapsed spoiler. Default: "Expand".
<U>collapsetext</U> - Link text for the expanded spoiler. Default: "Collapse".

<U>Example:</U>

<PRE>(:spoiler expandtext="More..." collapsetext="Less" inline :)
Text
(:spoilerend:)</PRE>
 Collapse Collapse text (:spoiler:) Expand http://jenyay.net/Outwiker/SpoilerEn Project-Id-Version: outwiker
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2014-10-03 21:44+0400
PO-Revision-Date: 2016-08-16 16:39+0300
Last-Translator: Jenyay <jenyay.ilin@gmail.com>
Language-Team: Swedish
Language: sv_SE
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 1.8.8
X-Crowdin-Project: outwiker
X-Crowdin-Language: sv-SE
X-Crowdin-File: spoiler.pot
 Lägg till kommandot (:spoiler:) i wiki-tolken.

<B>Användning:</B>
<PRE>(:spoiler:)
Text
(:spoilerend:)</PRE>

För inkapslad spoiler-användning (:spoiler0:), (:spoiler1:)... (:spoiler9:). 

<U>Exempel:</U>

<PRE>(:spoiler:)
Text
&nbsp;&nbsp;&nbsp;(:spoiler1:)
&nbsp;&nbsp;&nbsp;Nested spoiler
&nbsp;&nbsp;&nbsp;(:spoiler1end:)
(:spoilerend:)</PRE>

<B>Parametrar:</B>
<U>inline</U> - Spoilern kommer att vara i komprimerat läge.
<U>expandtext</U> - Länktext för komprimerad spoiler. Standard: "Expandera".
<U>collapsetext</U> - Länktext för expanderad spoiler. Standard: "Komprimera".

<U>Exempel:</U>

<PRE>(:spoiler expandtext="Mer..." collapsetext="Mindre" inline :)
Text
(:spoilerend:)</PRE>
 Komprimera Komprimera text (:spoiler:) Expandera http://jenyay.net/Outwiker/SpoilerEn 