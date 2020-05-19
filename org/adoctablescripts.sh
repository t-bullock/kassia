print-every-nth-line ()
{
    read -d '' STDIN 
    START_LINE="$1"
    LINE_INTERVAL="$2"
    echo "$STDIN" \
        | sed -n "${START_LINE}~${LINE_INTERVAL}p"
}

print-column ()
{
    read -d '' STDIN 
    COLUMN="$1"
    START_LINE="$(echo "${COLUMN}+4" | bc)"
    echo "$STDIN"                               \
        | print-every-nth-line "$START_LINE" 11 \
        | sed 's/^|//'
}

check-for-duplicates ()
{
    read -d '' STDIN 
    COLUMN="$1"
    SORTED_COLUMN_OUTPUT="$(echo "$STDIN"       \
        | print-column "$COLUMN"                \
        | sort | grep -v '^$')"
    diff <(echo $SORTED_COLUMN_OUTPUT | uniq) \
         <(echo $SORTED_COLUMN_OUTPUT)
}
