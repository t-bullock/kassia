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
    #local START_LINE="$(echo "${COLUMN}+4" | bc)"
    echo "$STDIN"                               \
        | python adoctablescripts.py            \
                print-column "$COLUMN"
    #    | print-every-nth-line "$START_LINE" 11 \
    #    | sed 's/^|//'
}

check-for-duplicates ()
{
    local STDIN=""
    read -r -d '' STDIN 
    local COLUMN="$1"
    local SORTED_COLUMN_OUTPUT="$(echo "$STDIN" \
        | python adoctablescripts.py            \
                 print-column "$COLUMN"         \
        | tail -n +1 |sort | grep -v '^\s*$')"
    diff <(echo $SORTED_COLUMN_OUTPUT | uniq) \
         <(echo $SORTED_COLUMN_OUTPUT)
}
