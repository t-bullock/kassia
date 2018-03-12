Kassia
======
Kassia is a scoring program for creating music written in Byzantine notation. It takes an XML file (schema file to be released later), parses the neumes and lyrics, and generates a formatted PDF using [ReportLab](http://www.reportlab.com).

An example XML file with the available options is shown below.

```xml
<bnml top_margin="50" bottom_margin="50" left_margin="60" right_margin="60" line_height="70" char_spacing="3">
    <identification>
        <!-- These show up in the properties of the pdf file. -->
        <work-title>God is the Lord</work-title>
        <author type="composer">Trevor Bullock</author>
        <rights>Copyright John Doe 2018</rights>
    </identification>
    <defaults>
        <page-layout>
            <!-- How far the lyrics are below a line of neumes. -->
            <lyric-y-offset>23</lyric-y-offset>
            <!-- Other page sizes are: legal and A4, but this has bugs. For now use letter size -->
            <paper-size>letter</paper-size>
        </page-layout>
        <!-- Default neume font family, size, color, etc. For now you're stuck with Kassia Tsak Main, but you can change the size and color. -->
        <neume-font font_family="Kassia Tsak Main" font_size="30" color="#000000" />
        <!-- Change font_family to any font you have placed in your kassia/pdfmaker/fonts folder. -->
        <lyric-font font_family="Helvetica" font_size="14" color="#000000" />
        <!-- Same as the lyric-font instructions. -->
        <dropcap-font font_family="ATHONITE" font_size="45" color="#cf232b" />
        <!-- Same. -->
        <paragraph-font font_family="Helvetica" font_size="14" color="#000000" align="left" />
    </defaults>

    <!-- Titles can be created like this. -->
    <paragraph align="center" font_family="ATHONITE" font_size="30">God is the Lord</paragraph>

    <!-- Here's our main martyria. -->
    <paragraph align="center" font_family="Times New Roman">
        Mode
        <font font_family="Kassia Tsak Martyria" font_size="30">P</font>
        Ζω
        &#160;
        <font font_family="Kassia Tsak Main" font_size="18">5</font>
    </paragraph>

    <troparion>
        <neumes>
            0 d ! 1 q ! 0 ! 1 n ! ! 1 1 a
        </neumes>
        <!-- Any time you want to specify some nuemes that have an attribute different than the defaults at the top of this file, you'll need to specify them like this. Here we use a different font for Martyria and we're making it red. -->
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            r $
        </neumes>
        <neumes>
            p S ! ! 1 n ! ! s 0 ! w S ! ! ! s
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            y ^
        </neumes>
        <dropcap>
            G
        </dropcap>
        <lyrics>
            God is the Lord &amp; has re- vealed Him- self to us
            bles- - sed is he who comes in the name of the Lord
        </lyrics>
    </troparion>

    <!-- Paragraphs automatically wrap text -->
    <paragraph top_margin="75">
        Verse 1: Give thanks to the Lord, for He is good, for His mercy endures forever.
    </paragraph>
    <paragraph>
        Verse 2: All the nations have surrounded me, but in the name of the Lord, I have overcome them.
    </paragraph>
    <paragraph>
        Verse 3: This has been done by the Lord, and it is wonderful in our eyes.
    </paragraph>

    <!-- Here we do a negative top margin to make this paragraph look like it's inline with the one before it -->
    <paragraph font_size="28" font_family="Kassia Tsak Martyria" color="#cf232b" align="right" top_margin="-20">
        q !
    </paragraph>

    <troparion>
        <!-- Notice for a jump of three, the klasma goes first, then the kentima. This way the klasma is properly centered. -->
        <neumes>
            1 a ~ ! 1 q ! 0 1 1 n ! ! ! ! s
        </neumes>
        <!-- Here we have a custom font and color, outside the neume default at the top of the file -->
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            y ^
        </neumes>
        <neumes>
            0 z
        </neumes>
        <neumes font_family="Kassia Tsak Chronos" color="#cf232b">
            z
        </neumes>
        <neumes>
            0 1 1 n ! ! s 0 ! w A ! ! / 0 ! F
        </neumes>
        <neumes font_family="Kassia Tsak Martyria" color="#cf232b">
            y ^
        </neumes>
        <dropcap>
            G
        </dropcap>
        <lyrics>
            God is the Lord &amp; has re- vealed Him- self to us
            bles- - sed is he who comes in the name of the Lord _
        </lyrics>
    </troparion>

    <!-- Use pagebreak to force eveyrthing below it to a new page -->
    <pagebreak />

    <troparion>
    <!-- Another hymn. -->
    </troparion>

</bnml>
```
## Typing with Kassia Fonts
Kassia Main Font
![Kassia Keyboard Layout](kassia_layout_main.png?raw=true)