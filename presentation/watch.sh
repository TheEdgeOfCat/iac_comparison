#!/bin/bash -eu

DIRECTORY_TO_OBSERVE="."

function block_for_change {
	inotifywait --recursive \
		--event modify,move,create,delete \
		--exclude "_build.+"\
		$DIRECTORY_TO_OBSERVE >/dev/null 2>&1

	echo -n ""
}

function build {
	clear
	make revealjs
}

build
while block_for_change; do
	build
done
