dir=$(dirname "$0")
web_dir="$dir/code"
data_dir="$web_dir/data"
dump_dir="$data_dir/extracted"

echo "Downloading WCA Database"
curl https://www.worldcubeassociation.org/results/misc/WCA_export.tsv.zip -o "$data_dir/WCA_export.tsv.zip"

if [ -e "$dump_dir/metadata.json" ]
then
    mv "$dump_dir/metadata.json" "$dump_dir/previous_metadata.json"
fi

echo "Unzipping archive"
unzip -o "$data_dir/WCA_export.tsv.zip" -d "$dump_dir"

echo "Importing WCA data"
python "$web_dir/manage.py" runscript import_wca_data