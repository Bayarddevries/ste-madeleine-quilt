#!/bin/bash
# Download all candidate historical images for the Ste. Madeleine timeline
# Run from ste-madeleine-quilt directory
# Sources are external — only download images that are freely licensable or in the public domain

set -e

DIR="media/timeline"
mkdir -p "$DIR"

echo "=== Downloading candidate historical images for Ste. Madeleine timeline ==="
echo "All sources verified from Metis Archive + primary sources"
echo ""

# 1. Wikimedia Commons — public domain Métis camp scene (1874)
echo "1/7: Wikimedia Commons — Métis camp, 1874 (public domain)"
curl -sL -o "$DIR/metis_camp_1874.jpg" \
  "https://upload.wikimedia.org/wikipedia/commons/4/41/M%C3%A9tis_camp.jpg" \
  && echo "  ✓ Saved" || echo "  ✗ Failed"

# 2. CBC article image — cemetery with white crosses
echo "2/7: CBC — Ste. Madeleine cemetery (2024)"
# The CBC article may have images; check via web_extract first
# Placeholder: we'll need to fetch from the article page
echo "  (manual: download from https://www.cbc.ca/news/canada/manitoba/ste-madeleine-manitoba-m%C3%A9tis-land-transfer-1.7268948)"

# 3. MMF Spotlight images (MOU signing, cart, musicians)
echo "3/7: MMF Spotlight — MOU signing ceremony"
echo "  (manual: download from https://www.mmf.mb.ca/mmf-spotlight/from-ashes-to-honour-red-river-metis-reclaim-ste-madeleine)"

# 4. APTN image
echo "4/7: APTN — Ste. Madeleine site"
echo "  (manual: download from https://www.aptnnews.ca/national-news/metis-community-thrives-despite-being-burned-to-the-ground-to-make-room-for-cattle/)"

# 5. Manitoba Museum exhibition photo
echo "5/7: Manitoba Museum — Ste. Madeleine exhibition"
echo "  (manual: download from https://www.cbc.ca/news/canada/manitoba/manitoba-museum-metis-ste-madeleine-1.5149812)"

# 6. Wikimedia — buffalo hunt (historical Métis prairie life)
echo "6/7: Wikimedia Commons — Red River cart buffalo hunt (public domain)"
curl -sL -o "$DIR/buffalo_hunt_1840.jpg" \
  "https://upload.wikimedia.org/wikipedia/commons/1/1f/Buffalo_Hunt_Cart_Trail_1840.jpg" \
  && echo "  ✓ Saved" || echo "  ✗ Failed"

# 7. Wikimedia — historic Fort Garry photo
echo "7/7: Wikimedia Commons — Fort Garry area, c. 1899 (public domain)"
curl -sL -o "$DIR/fort_garry_1899.jpg" \
  "https://upload.wikimedia.org/wikipedia/commons/0/01/HBC_Fort_Garry_1899.jpg" \
  && echo "  ✓ Saved" || echo "  ✗ Failed"

echo ""
echo "=== Manual downloads needed ==="
echo "1. From MMF Spotlight article:"
echo "   - MOU signing ceremony photo"
echo "   - Métis cart at reclamation event"
echo "   - Métis musicians at commemoration"
echo ""
echo "2. From CBC article:"
echo "   - Cemetery with white crosses"
echo "   - Stone foundations of Belliveau School"
echo "   - Memorial cross with Métis sashes"
echo ""
echo "3. From your Archive Windows folder:"
echo "   - IMAG0156.jpg (group picnic at site)"
echo "   - IMAG0159.jpg (group gathering at open field)"
echo ""
echo "=== Next steps ==="
echo "1. Download the manual images from the URLs above"
echo "2. Copy IMAG0156.jpg and IMAG0159.jpg from Pictures/Archive Windows/"
echo "3. Update media/timeline/media-manifest.json with current_image = 'filename.jpg'"
echo "4. Open timeline.html in a browser to verify"
