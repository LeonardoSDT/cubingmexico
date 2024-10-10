#!/usr/bin/env sh

dir=$(dirname "$0")
web_dir="$dir/code"

echo "Downloading WCA Database 2"
wget --header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" \
         --referer="https://www.worldcubeassociation.org" \
         -O "/tmp/WCA_export.tsv.zip" \
         https://www.worldcubeassociation.org/export/results/WCA_export.tsv

echo "Unzipping archive"
unzip -o "/tmp/WCA_export.tsv.zip" -d "/tmp"

echo "Importing WCA data"
python "$web_dir/manage.py" runscript import_wca_data