# Kassia

Kassia is a scoring program for creating music written in Byzantine notation. It takes an XML file (schema file to be released later), parses the neumes and lyrics, and generates a formatted PDF using [ReportLab](https://www.reportlab.com).

## Requirements

Python 3.7

## Setup

1. Install Python 3.7
2. Make sure pip is installed by running ```which pip```
3. Install necessary packages by running ```pip install -r requirements.txt```
4. To generate a test pdf file run ```python  kassia.py sample.xml sample.pdf```

Either [pipenv](https://pipenv.pypa.io/en/latest) or [poetry](https://python-poetry.org/) is probably a better alternative to pip and requirements.txt.

## Running Kassia

```python kassia.py [input_xml_file] [output_file]```

## Editing with Kassia

Take a look at the contents of [sample.xml](sample.xml).

## Typing with Kassia Fonts

Kassia utilizes 5 fonts: Main, Combo, Chronos, Martyria, Fthora.

- Main has the most commly used neumes
- Combo has large jumps and large jumps with a kentimata
- Chronos has time modifying neumes like gorga and argon
- Martyria has martyries
- Fthora has fthores, chroes, sharps, and flats

For more information on typing out scores and how these fonts are used, see [KA New Stathis](https://github.com/t-bullock/KA-New-Stathis).
