#!/usr/bin/env sh

dir=$(dirname "$0")
web_dir="$dir/code"

echo "Determining State of the Commpetitions"
python "$web_dir/manage.py" runscript determine_competition_state