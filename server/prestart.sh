#! /bin/bash
echo "Fetching data from object store..."
python /app/scripts/download_data.py
echo "Filling database tables..."
python /app/scripts/fill_tables.py &