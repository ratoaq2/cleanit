#!/bin/bash
# Record docs/images/demo.gif with VHS in a container.
# Usage: scripts/demo.sh
# The tape cleans a copy of scripts/demo/movie.en.srt. See the demo-gif skill.

set -e

# Git Bash: do not change the container paths into Windows paths
export MSYS_NO_PATHCONV=1

repo=$(pwd -W 2>/dev/null || pwd)
engine=$(command -v podman || command -v docker)

# Podman on WSL: crun fails with "controller `pids` is not available". The demo needs no cgroup limits.
run_args=()
if [[ "$engine" == *podman* ]]; then run_args=(--cgroups=disabled); fi

"$engine" build -q -t localhost/cleanit:latest .
"$engine" build -q -t localhost/cleanit-vhs -f scripts/demo.Dockerfile .
"$engine" run --rm "${run_args[@]}" -v "$repo:/repo" -w /repo localhost/cleanit-vhs scripts/demo.tape
