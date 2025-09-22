set -euo pipefail

API_URL="https://aviationweather.gov/api/data/metar"
OUTPUT_DIR="raw_metars"
AIRPORT_CODES_FILE="airport_codes.txt"

mkdir -p "$OUTPUT_DIR"
echo "Fetching METAR data for airports..."

while read -r airport_code; do
  [ -z "$airport_code" ] && continue

  URL="$API_URL?ids=$airport_code&format=json"
  OUT="$OUTPUT_DIR/${airport_code}.json"

  echo "  -> Fetching data for $airport_code..."
  curl -s "$URL" -o "$OUT" 2>&1

  if [ ! -s "$OUT" ] || [ "$(jq 'length' "$OUT")" -eq 0 ]; then
    echo "Warning: No METAR data for $airport_code" >&2
  else
    echo "  -> Data for $airport_code saved."
  fi
done < "$AIRPORT_CODES_FILE"

echo "Data fetching complete. Check '$OUTPUT_DIR'."
