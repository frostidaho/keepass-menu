#!/bin/bash
SCRIPT=$(readlink -f "$0")
PROJDIR=$(dirname $(dirname "$SCRIPT"))
DATADIR="$PROJDIR/tests/data"

db="keepassx_onlykey"
keepass-menu\
    --filename+keyfile $DATADIR/$db.kdbx $DATADIR/$db.key\
    "$@"

