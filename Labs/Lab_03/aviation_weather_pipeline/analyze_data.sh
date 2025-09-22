#!/usr/bin/env bash
set -euo pipefail

RAW_DATA_DIR="raw_metars"
OUTPUT_FILE="weather_report.csv"

echo "ICAO,ObservationTime,WindDirection,WindSpeed,TemperatureC,FlightCategory" > "$OUTPUT_FILE"
echo "Analyzing METAR data..."

for json_file in "$RAW_DATA_DIR"/*.json; do
  [ -f "$json_file" ] || continue
  if [ "$(jq 'length' "$json_file")" -gt 0 ]; then
    jq -r '.[0] | [.icaoId,.reportTime,.wdir,.wspd,.temp,.fltCat] | @csv' "$json_file" >> "$OUTPUT_FILE"
  else
    echo "Warning: Empty file $json_file" >&2
  fi
done

echo "Analysis complete. Results in '$OUTPUT_FILE'."
