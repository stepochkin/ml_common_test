#!/bin/bash

set -e

SPATH=$(readlink -f $(dirname $0))

cd ${SPATH}
python $(which nose2) -v
