#!/bin/bash
SCRIPT=$(readlink -f "$0")
PROJDIR=$(dirname $(dirname "$SCRIPT"))
DATADIR="$PROJDIR/tests/data"

db="db2"
echo "EXAMPLE SCRIPT: password for $db is 'testpass1234'"
echo "EXAMPLE SCRIPT: the menu should display 2 entries"
keepass-menu\
    --filename $DATADIR/$db.kdbx\
    --pw-query tk\
    --output autotype_tab\
    "$@"

