#!/bin/bash
SCRIPT=$(readlink -f "$0")
PROJDIR=$(dirname $(dirname "$SCRIPT"))
DATADIR="$PROJDIR/tests/data"

db="exampledatabase"
echo "EXAMPLE SCRIPT: password for $db is 'pass'"
echo "EXAMPLE SCRIPT: the menu should display 6 entries"
keepass-menu\
    -f+k $DATADIR/$db.kdbx $DATADIR/$db.key\
    "$@"

