#!/usr/bin/env sh

dir=$(dirname "$0")
web_dir="$dir/code"

echo "Downloading WCA Database"
curl -L https://www.worldcubeassociation.org/export/results/WCA_export.tsv.zip -o "/tmp/WCA_export.tsv.zip"

echo "Unzipping archive"
unzip -o "/tmp/WCA_export.tsv.zip" -d "/tmp"

echo "Importing WCA data"
python "$web_dir/manage.py" runscript import_wca_data