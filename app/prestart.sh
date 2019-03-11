#! /bin/bash
echo "Fetching data from object store..."
python /app/scripts/download_data.py
python /app/scripts/compute_genes.py &
python /app/scripts/convert_data.py &