# Kassia

Kassia is a scoring program for creating music written in Byzantine notation. It takes an XML file (schema file to be released later), parses the neumes and lyrics, and generates a formatted PDF using [ReportLab](https://www.reportlab.com).

## Requirements

Python 3.7

## Setup

1. Install Python 3.7
2. Make sure pip is installed by running ```which pip```
3. Install necessary packages by running ```pip install -r requirements.txt```
4. Re-create the sample score in /examples to make sure everything runs properly ```python  kassia.py examples/sample.xml examples/sample.pdf```

Note: [pipenv](https://pipenv.pypa.io/en/latest) or [poetry](https://python-poetry.org/) is likely a better alternative to pip and requirements.txt.

## Running Kassia

```python kassia.py [input_xml_file] [output_file]```

The examples folder has sample scores for you to experiment with.

## Editing Scores

Scores are saved as xml files. Take a look at the contents of [sample.xml](examples/sample.xml).

## Fonts

Kassia utilizes 5 fonts for neume styles: Main, Combo, Chronos, Martyria, Fthora.

- Main has the most commly used neumes
- Combo has large jumps and large jumps with a kentimata
- Chronos has time modifying neumes like gorga and argon
- Martyria has martyries
- Fthora has fthores, chroes, sharps, and flats

Some sample fonts are included for lyric styling— Alegreya, EB Garamond, and Gentium Plus. Kassia will look in the /fonts folder and be able to use any TTF files you put there.

For more information on key combinations for neume fonts, see [KA New Stathis](https://github.com/t-bullock/KA-New-Stathis).
