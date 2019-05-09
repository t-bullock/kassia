# Kassia

Kassia is a scoring program for creating music written in Byzantine notation. It takes an XML file (schema file to be released later), parses the neumes and lyrics, and generates a formatted PDF using [ReportLab](http://www.reportlab.com).

## Requirements

Python 3.7

## Setup

1. Install Python 3.7
2. Make sure pip is installed by running ```which pip```
3. Install necessary packages by running ```pip install -r requirements.txt```
4. To generate a test pdf file run ```python  kassia.py sample.xml sample.pdf```

## Running Kassia

```python kassia.py [input_xml_file] [output_file]```

## Editing with Kassia

An example XML file with some of the available options is shown below.

```xml
<bnml top_margin="50" bottom_margin="50" left_margin="60" right_margin="60" line_height="70" char_spacing="4">
    <identification>
        <!-- These show up in the properties of the pdf file. -->
        <work-title>Vespers as chanted on the Holy Mountain</work-title>
        <author type="composer">Father Ephraim</author>
        <subject>A great subject goes here</subject>
    </identification>
    <defaults>
        <page-layout>
            <!-- How far the lyrics are below a line of neumes. -->
            <lyric-y-offset>25</lyric-y-offset>
            <!-- Other page sizes are: legal and A4, but this has bugs. For now use letter size -->
            <paper-size>letter</paper-size>
        </page-layout>
        <!-- Default neume font family, size, color, etc. For now you're stuck with Kassia Tsak Main, but you can change the size and color. -->
        <neume-font font_family="Kassia Tsak Main" font_size="30" color="#000000" />
        <!-- Change font_family to any font you have placed in your kassia/pdfmaker/fonts folder, or to a font you have installed. -->
        <lyric-font font_family="Alegreya-Medium" font_size="14" color="#000000" />
        <!-- Same as the lyric-font instructions. If you have something like the Athonite font installed, you may want to specify that for the font_family here. -->
        <dropcap-font font_family="Alegreya-Bold" font_size="45" color="#cf232b" />
        <!-- Same. See ReportLab documentation for more paragraph options (like first_line_indent). -->
        <paragraph-font font_family="Alegreya-Medium" font_size="14" color="#000000" align="left" first_line_indent="0"/>
    </defaults>

    <!-- Titles are a lot like paragraphs, but they are centered by default. Underneath the hood they are simple strings, meaning they don't have all the options that 'paragraph' has  -->
    <title font_family="Alegreya SC-Bold" font_size="30" color="#0000e6">
        First Mode
    </title>

    <!-- Here is an example of a title using paragraph. Default settings come from paragraph-font above. -->
    <paragraph align="center" font_size="16" color="#0000e6">
        Lord, I Have Cried
    </paragraph>

    <!-- Here's our main martyria signature. -->
    <paragraph align="center" color="#cf232b">
        Mode
        <font font_family="Kassia Tsak Martyria" font_size="30">i</font>
        Πα
        <font font_family="Kassia Tsak Fthora" font_size="18">œ</font>
    </paragraph>

    <!-- To make this paragraph inline with the one above it, we use a negative top margin. Eventually we'll find a better way to do this. -->
    <paragraph align="right" color="#cf232b" top_margin="-45">
        <font font_family="Kassia Tsak Martyria" font_size="30">v</font>
        84
    </paragraph>

    <paragraph align="right" color="#0000e6">
        Κύριε ἐκέκραξα
    </paragraph>

    <troparion>
        <neumes>
            / 1 ; 0 ! 1 Z n ! ! ! l !
        </neumes>
        <!-- Any time you want to specify some nuemes that have an attribute different than the defaults at the top of this file, you'll need to specify them like this. Here we use a different font for time symbols (gorgon) and we're making it red. -->
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            / P
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            1 w ! s ,
        </neumes>
        <!-- Here we use a different font for Martyria and we're making it red. -->
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            q !
        </neumes>
        <neumes>
            3 A X X
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            m
        </neumes>
        <neumes>
            ! _ 1 j
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            z
        </neumes>
        <!-- Notice here that a different type of klasma is placed on the ison for better alignment -->
        <neumes>
            ! 0 d
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            q !
        </neumes>
        <neumes>
            1 a ' ! s p S / L 1 z Z
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            x
        </neumes>
        <neumes>
            / ! s -
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            1 j
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            z
        </neumes>
        <neumes>
            ! 0 d
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            q !
        </neumes>
        <!-- Notice that for this jump of three, the klasma goes between the oligon and kentima for proper alignment. -->
        <neumes>
            1 a ~ 0 1 Z n
        </neumes>
        <!-- A flat. -->
        <neumes font_family="Kassia Tsak Fthora" color="#cf232b">
            _
        </neumes>
        <neumes>
            ! ! Q S _ ` Z
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            x
        </neumes>
        <neumes>
            ! F
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            e #
        </neumes>
        <neumes>
            x n ! ! ! s ! l !
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            / 1 -
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            f
        </neumes>
        <neumes>
            1 a
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            y ^
        </neumes>
        <neumes>
            4 q S ! ! 1 1 n -
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            ! / L
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            1 1 a Z
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            x
        </neumes>
        <neumes>
            ! Z / ! s -
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            1 j
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            z
        </neumes>
        <neumes>
            ! 0 d
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            q !
        </neumes>
        <neumes>
            1 ~ 1 Z n
        </neumes>
        <neumes font_family="Kassia Tsak Fthora" color="#cf232b">
            _
        </neumes>
        <neumes>
            ! ! Q S _ ` w ! F
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            e #
        </neumes>
        <!-- Notice the special klasma after the synechis elaphron for better alignment. -->
        <neumes>
            0 ` 0 d Q S _ å 1 ` q M !
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            / 0 d -
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            v
        </neumes>
        <neumes>
            1 j
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            z
        </neumes>
        <neumes>
            ! 0 f
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            q !
        </neumes>
        <dropcap>
            L
        </dropcap>
        <!-- You can break the text into lines if it makes it easier to read. Kassia doesn't care. Here I start a new line whenever there's a martyria. -->
        <lyrics>
            Lord _ I have cried _ _ un- - to _ Thee _
            heark- en un- - to _ _ me
            heark- en un- to me _ _ O _ _ _ Lord
            Lord I have cried _ _ un- to _ Thee _
            heark- en _ un- to _ me _ _
            at- tend to the voice _ _ _ of _ my sup- - pli- ca- - - - tion
            when I cry _ _ un- to _ Thee _
            Heark- - en un- to me _ _ _ O _ _ _ Lord
        </lyrics>
    </troparion>

    <!-- Use linebreak to force a new line. -->
    <linebreak />

    <!-- Paragraphs automatically wrap text. Alternatively we could set a value to top_margin to push this paragraph down. -->
    <paragraph>
        Verse 1: Set, O Lord, a watch before my mouth, and a door of enclosure round about my lips.
    </paragraph>
    <paragraph>
        Verse 2: Incline not my heart to words of evil, to make excuses with excuses in sins.
    </paragraph>
    <paragraph>
        Verse 3: With men that work iniquity; and I will not join with their chosen.
    </paragraph>

    <!-- Use pagebreak to force eveyrthing below it to a new page. -->
    <pagebreak />

    <troparion>
    <!-- Another hymn. -->
    </troparion>

</bnml>
```
## Typing with Kassia Fonts

Kassia utilizes 5 fonts: Main, Combo, Chronos, Martyria, Fthora.

- Main has the most commly used neumes
- Combo has large jumps and large jumps with a kentimata
- Chronos has time modifying neumes like gorga and argon
- Martyria has martyries
- Fthora has fthores, chroes, sharps, and flats

Kassia Main Font
![Kassia Keyboard Layout](kassia_layout_main.png?raw=true)
