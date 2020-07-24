#!/bin/bash

PYTHON_FILES="../setup-gui/*.py ../setup-gui/stacks/*.py"
PROJECT=lliurex-openmeetings-setup
POTFILE=$PROJECT/$PROJECT.pot

mkdir -p $PROJECT

xgettext $PYTHON_FILES -o $POTFILE

