#! /bin/sh
while read f
do
    NUMBERBOYS="$(echo "$f" | awk '{ printf "%03d", $1 }')"
    NUMBERBOYS="$(echo "$NUMBERBOYS" - 1 | bc | awk '{ printf "%03d", $1 }')" 
    CHARBOYS="$(echo "$f" | awk '{ print $2 }' | sed -e 's,/,\slash,')"
    rm "main${NUMBERBOYS}.png"
done < <(awk -F "|" '{ print $3 }' ../neume_names_phase1.org | tail -n +3 | head -104 | sed -e 's/\\vert/|/' -e 's/\\`/`/' -e 's/\\/\\\\/' | nl)
