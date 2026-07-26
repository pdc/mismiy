#! /bin/sh -e
# Prepare images for site.

# Conversion from SVG via a macOS builtin command I never heard of before!
sips -s format png  assets/2026-07-20/enclosed-light.svg -o static/logo.144.png
cp assets/2026-07-20/enclosed-thin.svg static/enclosed-thin.svg
cp assets/2026-07-20/enclosed-light.svg static/enclosed.svg

# Apple likes big icons,
sed s/360px/180px/g assets/2026-07-20/borderless.svg > tmp.svg;  sips -s format png tmp.svg -o static/icon.180.png

# The mini versions need the lines thickend to show up properly.
sed -e s/360px/32px/g -e 's/"2"/"4"/g' assets/2026-07-20/borderless.svg > tmp.svg;  sips -s format png tmp.svg -o static/icon.32.png
sed -e s/360px/16px/g -e 's/"2"/"8"/g' assets/2026-07-20/borderless.svg > tmp.svg;  sips -s format png tmp.svg -o static/icon.16.png
cp assets/2026-07-20/borderless.svg static/icon.svg

# Pictures
mkdir -p static/pics/2026-07-26
cp  assets/2026-07-26/logo-tada.svg static/pics/2026-07-26
