print-every-nth-line ()
{
    read -r -d '' STDIN 
    local START_LINE="$1"
    local LINE_INTERVAL="$2"
    echo "$STDIN" \
        | sed -n "${START_LINE}~${LINE_INTERVAL}p"
    unset STDIN
}

print-column ()
{
    read -r -d '' STDIN 
    local COLUMN="$1"
    local START_LINE="$(echo "${COLUMN}+4" | bc)"
    echo "$STDIN"                               \
        | print-every-nth-line "$START_LINE" 11 \
        | sed 's/^|//'
    unset STDIN
}

check-for-duplicates ()
{
    read -r -d '' STDIN 
    local COLUMN="$1"
    local SORTED_COLUMN_OUTPUT="$(echo "$STDIN"       \
        | print-column "$COLUMN"                \
        | sort | grep -v '^$')"
    diff <(echo $SORTED_COLUMN_OUTPUT | uniq) \
         <(echo $SORTED_COLUMN_OUTPUT)
    unset STDIN
}
