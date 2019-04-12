#!/usr/bin/env bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"

set -eo pipefail

# #################
# Functions
#
function usage() {
  cat - <<-EOF

	usage: ./$me

	Mounts the project into a python:3.6 container and runs pytest

	This script more closely emulates what happens in the Travis-CI build server,
	and can be used to help reproduce errors that only occur in Travis.
	Such errors should be rare, but have occurred before.
	EOF
}

function log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >/dev/stderr
}

function die() {
  log "ERROR: $*"
  exit 1
}

# ###############
# Arguments
#
me="$(basename "$0")"

while getopts "h" opt; do
  case "$opt" in
    h) usage; exit 0;;
    *) usage; exit 1;;
  esac
done
shift $((OPTIND-1))

# No arguments - throw if any are specified
if [[ -n "$1" ]]; then
  die "ERROR: This script takes no arguments. Run with '$me -h' for help"
fi

# ###############
# Main
#

# 0. Create a temp file for saving the built image id
image_id_file=$(mktemp)
# shellcheck disable=SC2064
trap "rm -f $image_id_file" EXIT SIGINT

# 1. Build the image
log "Building image..."
CONTAINER_WORK_DIR="/app"
cd "$ROOT_DIR" && docker build --iidfile "$image_id_file" --file - "$ROOT_DIR" <<EOF
FROM python:3.6
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && apt-get update \
 && apt-get install -y \
      libgconf2-4 \
      ./google-chrome-stable_current_amd64.deb \
 && rm ./google-chrome-stable_current_amd64.deb \
 && rm -rf /var/lib/apt/lists/*
RUN pip install pipenv
WORKDIR $CONTAINER_WORK_DIR
ADD Pipfile .
ADD Pipfile.lock .
RUN pipenv install --dev
ENTRYPOINT ["pipenv", "run"]
CMD ["test"]
EOF
image_id="$(cat "$image_id_file")"
log "Image built! ID=$image_id"

# 2. Run the tests
log "Running tests in container..."
docker run --rm -it \
  -v "$ROOT_DIR:$CONTAINER_WORK_DIR" \
  "$image_id"
