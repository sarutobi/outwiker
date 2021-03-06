��          L      |       �   �  �      C     L     f  $   m  �  �  �       �     �     �  $   �                                         Add command (:spoiler:) in wiki parser.

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
PO-Revision-Date: 2014-10-03 21:44+0300
Last-Translator: Eugeniy Ilin <jenyay.ilin@gmail.com>
Language-Team: Italian
Language: it_IT
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 1.5.4
 Aggiunge il comando (:spoiler:) nel parser wiki.

<B>Utilizzo:</B>
<PRE>(:spoiler:)
Text
(:spoilerend:)</PRE>

Per spoiler nidificati usare i comandi (:spoiler0:), (:spoiler1:)... (:spoiler9:). 

<U>Esempio:</U>

<PRE>(:spoiler:)
Text
&nbsp;&nbsp;&nbsp;(:spoiler1:)
&nbsp;&nbsp;&nbsp;Nested spoiler
&nbsp;&nbsp;&nbsp;(:spoiler1end:)
(:spoilerend:)</PRE>

<B>Params:</B>
<U>inline</U> - Lo spoiler sarà in modalità allineata.
<U>expandtext</U> - Testo per lo spoilter ridotto. Default: "Expand".
<U>collapsetext</U> - Testo per lo spoilter espanso. Default: "Collapse".

<U>Esempio:</U>

<PRE>(:spoiler expandtext="More..." collapsetext="Less" inline :)
Text
(:spoilerend:)</PRE>
 Ridurre Riduci testo (:spoiler:) Espandi http://jenyay.net/Outwiker/SpoilerEn 