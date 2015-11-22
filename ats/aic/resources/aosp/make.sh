#!/bin/bash

set -e

. build/envsetup.sh

lunch "${1}"

shift

$MAKE "$@"

