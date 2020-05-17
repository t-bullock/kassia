#! /bin/sh

char-to-charname ()
{
    case "$1" in
        '$')  echo "dollarsign"               ;;
        '!')  echo "exclamation-point"        ;;
        '"')  echo "double-quote"             ;;
        '#')  echo "number-sign"              ;;
        '%')  echo "percent-sign"             ;;
        '&')  echo "ampersand"                ;;
        "'")  echo "single-quote"             ;;
        '(')  echo "left-paren"               ;;
        '*')  echo "asterisk"                 ;;
        '+')  echo "plus"                     ;;
        ',')  echo "comma"                    ;;
        '-')  echo "hyphen"                   ;;
        '.')  echo "period"                   ;;
        ':')  echo "colon"                    ;;
        ';')  echo "semicolon"                ;;
        '<')  echo "left-caret"               ;;
        '=')  echo "equal-sign"               ;;
        '>')  echo "right-caret"              ;;
        '?')  echo "question-mark"            ;;
        '@')  echo "at-sign"                  ;;
        '[')  echo "left-bracket"             ;;
        '\')  echo "backslash"                ;;
        ']')  echo "right-bracket"            ;;
        '^')  echo "up-caret"                 ;;
        '`')  echo "grave"                    ;;
        '{')  echo "left-curly-bracket"       ;;
        '|')  echo "pipe"                     ;;
        '}')  echo "right-curly-bracket"      ;;
        '~')  echo "tilde"                    ;;
        '«')  echo "left-double-caret"        ;;
        '˚')  echo "alternate-degree-sign"    ;;
        '‘')  echo "left-single-quote"        ;;
        '“')  echo "left-double-quote"        ;;
        '”')  echo "right-double-quote"       ;;
        '∂')  echo "derivative"               ;;
        '≠')  echo "unequal-sign"             ;;
        '/')  echo "slash"                    ;;
        '™')  echo "trademark"                ;;
        'Ω')  echo "capital-omega"            ;;
        'A')  echo "capital-A"                ;;
        'B')  echo "capital-B"                ;;
        'C')  echo "capital-C"                ;;
        'D')  echo "capital-D"                ;;
        'E')  echo "capital-E"                ;;
        'F')  echo "capital-F"                ;;
        'G')  echo "capital-G"                ;;
        'H')  echo "capital-H"                ;;
        'I')  echo "capital-I"                ;;
        'J')  echo "capital-J"                ;;
        'K')  echo "capital-K"                ;;
        'L')  echo "capital-L"                ;;
        'M')  echo "capital-M"                ;;
        'N')  echo "capital-N"                ;;
        'O')  echo "capital-O"                ;;
        'P')  echo "capital-P"                ;;
        'Q')  echo "capital-Q"                ;;
        'R')  echo "capital-R"                ;;
        'S')  echo "capital-S"                ;;
        'T')  echo "capital-T"                ;;
        'U')  echo "capital-U"                ;;
        'V')  echo "capital-V"                ;;
        'W')  echo "capital-W"                ;;
        'X')  echo "capital-X"                ;;
        'Y')  echo "capital-Y"                ;;
        'Z')  echo "capital-Z"                ;;
        'å')  echo "a-ring"                   ;;
        'ƒ')  echo "florin"                   ;;
         * )  echo "$1"                       ;;
    esac
}

 # Takes font name (prefix of png filenames) as argument
 # ie. "main"
rename-filenames-num-to-charname ()
{
    SUBFONT="$1"
    while read -r
    do

        NUMBERBOYS="$(echo "$f" | awk '{ printf "%03d", $1 }')"
        NUMBERBOYS="$(echo "$NUMBERBOYS" - 1 | bc | awk '{ printf "%03d", $1 }')" 
        CHARBOYS="$(echo "$f" | awk '{ print $2 }' | sed -e 's,/,\slash,')"
        CHARNAMEBOYS="$(char-to-charname "${CHARBOYS}")"
        echo mv "${SUBFONT}-${NUMBERBOYS}.png" "${SUBFONT}-${CHARNAMEBOYS}.png"

    done < <(awk -F "|" '{ print $3 }' ../neume_names_phase1.org \
                 | tail -n +3 | head -104 \
                 | sed -e 's/\\vert/|/' -e 's/\\`/`/' \
                 | nl)

}

# Takes font name (prefix of png filenames) as argument
# ie. "main"
rename-filenames-char-to-charname ()
{
    SUBFONT="$1"
    while read -r f
    do
        CHARBOYS="$(echo "$f" | sed -e "s/${1}-//" -e 's/\.png//')"
        CHARNAMEBOYS="$(char-to-charname "${CHARBOYS}")"
        echo mv "$f" "main-${CHARNAMEBOYS}.png"
    done < <(ls -A1 . | grep '\.png$')

}

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Only works for main font, needs to be
# modified to work with the other subfonts
# Requires ImageMagick to be installed
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
big-svg-to-small-pngs () 
{
    convert -crop '100%x0.95%' ~/Documents/prog/python3/kassia/org/ka_fontimages/main.svg '1.png'
}
