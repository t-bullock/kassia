print-every-nth-line ()
{
    local STDIN=""
    read -r -d '' STDIN 
    local START_LINE="$1"
    local LINE_INTERVAL="$2"
    echo "$STDIN" \
        | sed -n "${START_LINE}~${LINE_INTERVAL}p"
}

print-column ()
{
    local STDIN=""
    read -r -d '' STDIN 
    local COLUMN="$1"
    local START_LINE="$(echo "${COLUMN}+4" | bc)"
    echo "$STDIN"                               \
        | print-every-nth-line "$START_LINE" 11 \
        | sed 's/^|//'
}

check-for-duplicates ()
{
    local STDIN=""
    read -r -d '' STDIN 
    local COLUMN="$1"
    local SORTED_COLUMN_OUTPUT="$(echo "$STDIN"       \
        | print-column "$COLUMN"                \
        | sort | grep -v '^$')"
    diff <(echo $SORTED_COLUMN_OUTPUT | uniq) \
         <(echo $SORTED_COLUMN_OUTPUT)
}

print-column-better () #Work in progress ******DON'T USE*******
{
    local COLUMN="$1"
    local FIELD_COUNT="9"
    local FIELD_COUNTPP="$(echo "${FIELD_COUNT}+1" | bc)"
    local DELIMETER="|"
    local STDIN=""
    read -r -d '' STDIN
    STDIN="$(echo "$STDIN" | tr -d '\n' | sed 's/\\|/\\pipe/')"
    while [ "$(echo "$STDIN" | awk -F'|' '{ print NF }')" -ge "$FIELD_COUNT" ]
    do
        LINEBOYS="$(echo "${STDIN}" | cut -d"${DELIMETER}" --fields=-"${FIELD_COUNT}")"
        STDIN="$(echo "${STDIN}" | cut -d"${DELIMETER}" --fields="${FIELD_COUNTPP}-")"
        echo $LINEBOYS
    done
}
