#! /bin/sh
unset MV_GREENLIGHT
safe-mv ()
{
    if [ -z "${MV_GREENLIGHT}" ]
    then
        echo mv $@
    else
        mv $@
    fi
}

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
        '–')  echo "dash"                     ;;
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
        '_')  echo "underscore"               ;;
        '¨')  echo "diaeresis"                ;;
        '©')  echo "copyright"                ;;
        '®')  echo "restricted"               ;;
        '´')  echo "acute"                    ;;
        'ˆ')  echo "circumflex"               ;;
        '˜')  echo "small-tilde"              ;;
        '†')  echo "dagger"                   ;;
        '∆')  echo "capital-delta"            ;;
        '∑')  echo "capital-sigma"            ;;
        '√')  echo "sqrt"                     ;;
        '∫')  echo "integral"                 ;;
        '≈')  echo "almost-equal"             ;;
        '¥')  echo "yen"                      ;;
        'ç')  echo "c-cedilla"                ;;
        'œ')  echo "oe"                       ;;
        'ß')  echo "eszett"                   ;;
        'μ')  echo "mu"                       ;;
        'π')  echo "pi"                       ;;
         * )  echo $1                         ;;
    esac
}

 # Takes font name (prefix of png filenames) as argument
 # ie. "main"
rename-filenames-num-to-charname ()
{
    SUBFONT="$1"
    case "$SUBFONT" in
        "main"    ) RANGE_START=3   ; LENGTH=104  ;;
        "martyria") RANGE_START=109 ; LENGTH=71   ;;
        "fthora"  ) RANGE_START=182 ; LENGTH=79   ;;
        "combo"   ) RANGE_START=263 ; LENGTH=20   ;;
        "chronos" ) RANGE_START=285 ; LENGTH=44   ;;
        "archaia" ) RANGE_START=331 ; LENGTH=45   ;;
    esac
    while read -r f
    do

        NUMBERBOYS="$(echo "$f" | awk '{ printf "%03d", $1 }')"
        NUMBERBOYS="$(echo "$NUMBERBOYS" - 1 | bc | awk '{ printf "%03d", $1 }')" 
        CHARBOYS="$(echo "$f" | awk '{ print $2 }' | sed -e 's,/,\slash,')"
        CHARNAMEBOYS="$(char-to-charname "${CHARBOYS}")"
        safe-mv "${SUBFONT}-${NUMBERBOYS}.png" "${SUBFONT}-${CHARNAMEBOYS}.png"

    done < <(awk -F "|" '{ print $3 }' ../neume_names_phase1.org \
                 | tail -n +"$RANGE_START" | head -"$LENGTH" \
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
        safe-mv "$f" "${SUBFONT}-${CHARNAMEBOYS}.png"

    done < <(ls -A1 . | grep -e "^$SUBFONT.*\.png$")

}

# Takes font name (prefix of png filenames) as argument
# ie. "main"
big-svg-to-small-pngs () 
{
    SUBFONT="$1"
    case "$SUBFONT" in
        "main"    ) HEIGHT_PERCENT="0.96"               ;;
        "martyria") HEIGHT_PERCENT="1.05"         ;;
        "fthora"  ) HEIGHT_PERCENT="1.05"         ;;
        "combo"   ) HEIGHT_PERCENT="1.05"         ;;
        "chronos" ) HEIGHT_PERCENT="1.05"         ;;
        "archaia" ) HEIGHT_PERCENT="1.05"         ;;
    esac
    convert -crop "100%x${HEIGHT_PERCENT}%" \
            "${HOME}/Documents/prog/python3/kassia/org/ka_fontimages/${SUBFONT}.svg" \
            "${SUBFONT}.png"
    while read -r f
    do
        PREFIX="$(echo "$f" | awk -F '-' '{ print $1 }')"
        NUMBERBOYS="$(echo "$f" \
                    | awk -F '-' '{ print $2 }' \
                    | awk -F '.' '{ printf "%03d\n", $1 }')"
        safe-mv "$f" "${PREFIX}-${NUMBERBOYS}.png"
    done < <(ls -A1 . | grep -e "^$SUBFONT.*\.png$")
}
