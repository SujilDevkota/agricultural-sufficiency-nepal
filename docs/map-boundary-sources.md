# Interactive map boundary sources

The website's district map was updated on 19 October 2026 to include the northwestern extension (Limpiyadhura, Kalapani and Lipulekh) depicted in Nepal's revised 2020 map. This is a display-boundary update; it does not revise the submitted thesis, NSCA coverage, district statistics or spatial-analysis inputs. District shading represents the reported district aggregate, not separately measured values for the extension.

## Geometry and adaptation

- The existing 77-district layer carries 2017/2019 source metadata. The other 76 district geometries and Darchula's internal district boundaries are unchanged.
- The extension comes from [Acesmndr/nepal-geojson, DARCHULA.geojson](https://github.com/Acesmndr/nepal-geojson/blob/0e084221686fba8a4a8c1590661367676e96e473/generated-geojson/Province%207/Districts/DARCHULA.geojson), commit `0e084221686fba8a4a8c1590661367676e96e473`. This is a community-maintained display dataset, not an authoritative survey or international boundary determination.
- Adaptation used Shapely 2.2: repair the source polygon with `make_valid`; subtract the original Darchula polygon; retain the largest connected additional polygon (the northwestern extension); union it with original Darchula; use the exterior ring to remove two minute seam holes caused by differing source precision. No coordinates were drawn by hand. Other source differences were discarded.
- The resulting polygon is valid, contains original Darchula and does not overlap any other district. District IDs/names and all 77 data mappings are retained. Obsolete geometry measurements and dates were removed from the updated feature.

## Upstream license

MIT License

Copyright (c) 2018 Aashish Manandhar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
