/* Website data checked against the submitted thesis on 2026-09-23.
   District values reproduce Annex I, Table A1; summaries reproduce Chapter IV.
   Preserve published rounding when updating this presentation layer. */
window.THESIS = {
 "meta": {
  "title": "District-Level Patterns of Land Fragmentation, Irrigation Access, and Agricultural Production Sufficiency in Nepal",
  "author": "Sujil Devkota",
  "rollNo": "075/72",
  "institution": "Tribhuvan University · Patan Multiple Campus",
  "supervisor": "Kumar Bhattarai, Assistant Professor",
  "program": "M.A. Economics Thesis",
  "dataSource": "National Sample Census of Agriculture (NSCA) 2021/22",
  "districts": 77,
  "year": 2026,
  "citation": "Devkota, S. (2026). District-Level Patterns of Land Fragmentation, Irrigation Access, and Agricultural Production Sufficiency in Nepal [Master's thesis, Tribhuvan University]. Patan Multiple Campus.",
  "repoUrl": "https://github.com/SujilDevkota/agricultural-sufficiency-nepal",
  "contactEmail": "sujildevkota@gmail.com"
 },
 "keyStats": [
  {
   "label": "Districts analysed",
   "value": "77",
   "sub": "all of Nepal"
  },
  {
   "label": "Avg. holding size",
   "value": "0.54",
   "sub": "hectares per holding"
  },
  {
   "label": "Avg. parcels per holding",
   "value": "2.81",
   "sub": "fragmentation"
  },
  {
   "label": "Irrigated area share",
   "value": "52.5%",
   "sub": "weighted mean"
  },
  {
   "label": "Insufficient production",
   "value": "55.0%",
   "sub": "of holdings nationally"
  },
  {
   "label": "Irrigation ↔ insufficiency",
   "value": "−0.86",
   "sub": "weighted correlation"
  }
 ],
 "ranges": [
  {
   "name": "Parcels per holding",
   "min": "1.5",
   "max": "6.3",
   "minDistrict": "Lalitpur",
   "maxDistrict": "Humla"
  },
  {
   "name": "Irrigated area share (%)",
   "min": "2.9",
   "max": "91.1",
   "minDistrict": "Rukum East",
   "maxDistrict": "Bara"
  },
  {
   "name": "Insufficiency share (%)",
   "min": "31.9",
   "max": "86.9",
   "minDistrict": "Rupandehi",
   "maxDistrict": "Dolpa"
  }
 ],
 "objectives": [
  "Examine the district-level patterns of land fragmentation and irrigation access across the districts of Nepal.",
  "Examine the district-level patterns of agricultural production sufficiency across the districts of Nepal.",
  "Analyse the district-level relationship between land fragmentation, irrigation access, and agricultural production sufficiency — including whether irrigation access moderates the association between fragmentation and sufficiency."
 ],
 "hypotheses": [
  {
   "id": "H1",
   "text": "Districts with wider irrigation coverage report lower agricultural production insufficiency."
  },
  {
   "id": "H2",
   "text": "Districts with more fragmented holdings report higher agricultural production insufficiency."
  },
  {
   "id": "H3",
   "text": "Irrigation moderates the association between fragmentation and insufficiency — with the direction left open: irrigation and consolidation may act as substitutes or as complements."
  }
 ],
 "provinceProfile": [
  {
   "province": "Koshi",
   "parcels": 2.201,
   "irrigation": 0.542,
   "insufficiency": 0.559
  },
  {
   "province": "Madhesh",
   "parcels": 2.968,
   "irrigation": 0.743,
   "insufficiency": 0.43
  },
  {
   "province": "Bagmati",
   "parcels": 2.579,
   "irrigation": 0.393,
   "insufficiency": 0.559
  },
  {
   "province": "Gandaki",
   "parcels": 2.986,
   "irrigation": 0.376,
   "insufficiency": 0.65
  },
  {
   "province": "Lumbini",
   "parcels": 2.927,
   "irrigation": 0.561,
   "insufficiency": 0.51
  },
  {
   "province": "Karnali",
   "parcels": 3.353,
   "irrigation": 0.289,
   "insufficiency": 0.695
  },
  {
   "province": "Sudurpashchim",
   "parcels": 3.192,
   "irrigation": 0.562,
   "insufficiency": 0.599
  }
 ],
 "correlations": [
  {
   "variable": "Irrigated-area share",
   "value": -0.856
  },
  {
   "variable": "Irrigated-holdings share",
   "value": -0.751
  },
  {
   "variable": "Loan / credit access share",
   "value": -0.643
  },
  {
   "variable": "Avg. holding size",
   "value": -0.355
  },
  {
   "variable": "Power tiller share",
   "value": -0.102
  },
  {
   "variable": "Subsidy share",
   "value": -0.061
  },
  {
   "variable": "Fast market-access share",
   "value": 0.327
  },
  {
   "variable": "Avg. parcels per holding",
   "value": 0.396
  },
  {
   "variable": "Climate-impact share",
   "value": 0.466
  }
 ],
 "scenarios": [
  {
   "label": "Low irrigation · Low fragmentation",
   "predicted": 0.679
  },
  {
   "label": "Low irrigation · High fragmentation",
   "predicted": 0.699
  },
  {
   "label": "High irrigation · Low fragmentation",
   "predicted": 0.481
  },
  {
   "label": "High irrigation · High fragmentation",
   "predicted": 0.48
  }
 ],
 "methodology": [
  {
   "step": "1",
   "title": "Data construction",
   "body": "Merge NSCA 2021/22 district tables on parcel structure, irrigation, sufficiency, food-insufficiency duration, and six controls into one 77-district cross-section."
  },
  {
   "step": "2",
   "title": "Descriptive & correlation",
   "body": "Weighted means, dispersion, district extremes, and holdings-weighted correlations of each predictor with the insufficiency share."
  },
  {
   "step": "3",
   "title": "Weighted OLS benchmark",
   "body": "Linear baseline with the full control set and province fixed effects, weighted by number of holdings."
  },
  {
   "step": "4",
   "title": "Fractional logit (preferred)",
   "body": "Bounded-outcome model with province fixed effects and mean-centred interactions — the headline specification for a proportion in [0,1]."
  },
  {
   "step": "5",
   "title": "Average partial effects",
   "body": "Translate logit coefficients to interpretable marginal changes, plus scenario predictions with 999-replication bootstrap inference."
  },
  {
   "step": "6",
   "title": "Robustness battery",
   "body": "Belt vs. province effects, parsimonious specification, unweighted estimation, alternative measures, diagnostics, and the severe-insufficiency outcome."
  }
 ],
 "conclusions": [
  {
   "title": "Water access dominates structure",
   "body": "Across districts, irrigation coverage — together with the agro-ecology it reflects — is the clearest distinguishing factor between districts where farming feeds households and districts where it does not."
  },
  {
   "title": "Geography and irrigation are intertwined",
   "body": "Replacing province effects with Mountain/Hill/Terai controls attenuates the irrigation coefficient. The claim is conditional and descriptive, not causal — Nepal's irrigation gradient runs along its ecological geography."
  },
  {
   "title": "Fragmentation's bivariate gap is absorbed",
   "body": "The +0.40 raw correlation collapses to ~0 once location is held fixed. Consolidation alone is unlikely to deliver large sufficiency gains in unmechanised hill agriculture."
  },
  {
   "title": "Severe insufficiency is a different beast",
   "body": "The 10–12 month deprivation measure peaks in Kaski, Kathmandu and eastern Terai — near-landless holdings living from non-farm income, not the mountain districts. It is a distinct dimension of deprivation."
  }
 ],
 "limitations": [
  {
   "title": "Association, not causation",
   "body": "The site reports descriptive statistics, correlations, and model-based associations conditioned on geography. None shows that adding irrigation would, by itself, lower insufficiency by 20 points."
  },
  {
   "title": "Districts, not households",
   "body": "The unit of analysis is the district. A district mean can hide deep variation within it; nothing here speaks to which households inside a district are food-insufficient."
  },
  {
   "title": "Self-reported outcome",
   "body": "Insufficiency is what holders told NSCA enumerators about whether their own farm output covered household consumption. It is not a calorie or income measure."
  },
  {
   "title": "Fragmentation is proxied",
   "body": "Parcels-per-holding captures one dimension of fragmentation only. It ignores parcel dispersion and distance — both of which matter in hill agriculture."
  },
  {
   "title": "One census year",
   "body": "NSCA 2021/22 is a single cross-section taken during a COVID-affected reference period. The patterns may not generalise to other years."
  }
 ],
 "policy": [
  "Prioritise irrigation expansion and year-round water reliability in low-coverage hill and mountain districts.",
  "Pursue land consolidation, if at all, bundled with irrigation and mechanisation — not as a stand-alone remedy.",
  "Target chronic food deprivation beyond mountain agriculture: near-landless peri-urban and Terai holdings are invisible to production-based targeting.",
  "Equip provincial and local governments — now holding extension and local-irrigation mandates — with the district evidence for sub-national prioritisation."
 ],
 "glossary": [
  {
   "term": "Weighted correlation",
   "def": "A Pearson correlation in which each district is weighted by its number of holdings, so big farming districts count for more than tiny ones."
  },
  {
   "term": "Fractional logit",
   "def": "A regression for outcomes that live between 0 and 1 (like a share). It is the right tool when the outcome is a proportion rather than a count or amount."
  },
  {
   "term": "Province fixed effects",
   "def": "Province indicators, with one reference province. They account for shared province-level differences, so the remaining coefficients describe within-province variation."
  },
  {
   "term": "Average partial effect (APE)",
   "def": "The average change in predicted insufficiency for a one-unit change in a predictor, averaged across all 77 districts. The interpretable analogue of a logit coefficient."
  },
  {
   "term": "Bootstrap confidence interval",
   "def": "A range built by re-estimating the model on 999 district resamples. A 95% interval excluding zero supports a nonzero association under the model and resampling assumptions; it does not establish causation."
  },
  {
   "term": "Ecological belt",
   "def": "Nepal's three north-to-south agro-ecological zones: Mountain, Hill, Terai. A coarser geographic control than province."
  }
 ],
 "references": [
  {
   "authors": "Ali, D. A., Deininger, K., & Ronchi, L.",
   "year": 2019,
   "title": "Costs and benefits of land fragmentation: Evidence from Rwanda.",
   "journal": "World Bank Economic Review, 33(3)"
  },
  {
   "authors": "Khanal, U.",
   "year": 2018,
   "title": "Why are farmers keeping cultivatable lands fallow even though there is food scarcity in Nepal?",
   "journal": "Food Security, 10(3), 603–614"
  },
  {
   "authors": "Niroula, G. S., & Thapa, G. B.",
   "year": 2005,
   "title": "Impacts and causes of land fragmentation, and lessons learned from land consolidation in South Asia.",
   "journal": "Land Use Policy, 22(4)"
  },
  {
   "authors": "Papke, L. E., & Wooldridge, J. M.",
   "year": 1996,
   "title": "Econometric methods for fractional response variables with an application to 401(k) plan participation rates.",
   "journal": "Journal of Applied Econometrics, 11(6)"
  },
  {
   "authors": "Singh, I., Squire, L., & Strauss, J. (Eds.)",
   "year": 1986,
   "title": "Agricultural household models: Extensions, applications, and policy.",
   "journal": "Johns Hopkins University Press"
  },
  {
   "authors": "NSO Nepal.",
   "year": 2023,
   "title": "National Sample Census of Agriculture 2021/22 — National Report.",
   "journal": "National Statistics Office, Government of Nepal"
  }
 ],
 "severeContrast": [
  {
   "district": "Dolpa",
   "belt": "Mountain",
   "overall": 0.869,
   "severe": 0.001,
   "cited": true
  },
  {
   "district": "Manang",
   "belt": "Mountain",
   "overall": 0.866,
   "severe": 0.013,
   "cited": false
  },
  {
   "district": "Bajura",
   "belt": "Mountain",
   "overall": 0.857,
   "severe": 0.01,
   "cited": false
  },
  {
   "district": "Kaski",
   "belt": "Hill",
   "overall": 0.609,
   "severe": 0.163,
   "cited": true
  },
  {
   "district": "Kathmandu",
   "belt": "Hill",
   "overall": 0.676,
   "severe": 0.161,
   "cited": true
  },
  {
   "district": "Jhapa",
   "belt": "Terai",
   "overall": 0.463,
   "severe": 0.129,
   "cited": false
  },
  {
   "district": "Morang",
   "belt": "Terai",
   "overall": 0.442,
   "severe": 0.095,
   "cited": false
  },
  {
   "district": "Rupandehi",
   "belt": "Terai",
   "overall": 0.319,
   "severe": 0.035,
   "cited": false
  }
 ],
 "geoNameAliases": {
  "Chitawan": "Chitwan",
  "Kabhrepalanchok": "Kavrepalanchok",
  "Kapilbastu": "Kapilvastu"
 },
 "districts": [
  {
   "name": "Achham",
   "belt": "Hill",
   "province": "Sudurpashchim",
   "holdings": 45214,
   "parcels": 4.4,
   "irrigation": 0.323,
   "insufficiency": 0.771,
   "severe": 0.02,
   "rank": 12
  },
  {
   "name": "Arghakhanchi",
   "belt": "Hill",
   "province": "Lumbini",
   "holdings": 42418,
   "parcels": 3.2,
   "irrigation": 0.165,
   "insufficiency": 0.854,
   "severe": 0.073,
   "rank": 4
  },
  {
   "name": "Baglung",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 50802,
   "parcels": 3.2,
   "irrigation": 0.137,
   "insufficiency": 0.829,
   "severe": 0.06,
   "rank": 6
  },
  {
   "name": "Baitadi",
   "belt": "Hill",
   "province": "Sudurpashchim",
   "holdings": 47262,
   "parcels": 4.1,
   "irrigation": 0.146,
   "insufficiency": 0.756,
   "severe": 0.03,
   "rank": 18
  },
  {
   "name": "Bajhang",
   "belt": "Mountain",
   "province": "Sudurpashchim",
   "holdings": 35330,
   "parcels": 4.2,
   "irrigation": 0.337,
   "insufficiency": 0.827,
   "severe": 0.032,
   "rank": 7
  },
  {
   "name": "Bajura",
   "belt": "Mountain",
   "province": "Sudurpashchim",
   "holdings": 25279,
   "parcels": 5.3,
   "irrigation": 0.289,
   "insufficiency": 0.857,
   "severe": 0.01,
   "rank": 3
  },
  {
   "name": "Banke",
   "belt": "Terai",
   "province": "Lumbini",
   "holdings": 67885,
   "parcels": 2.2,
   "irrigation": 0.682,
   "insufficiency": 0.439,
   "severe": 0.067,
   "rank": 65
  },
  {
   "name": "Bara",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 84138,
   "parcels": 2.7,
   "irrigation": 0.911,
   "insufficiency": 0.369,
   "severe": 0.023,
   "rank": 72
  },
  {
   "name": "Bardiya",
   "belt": "Terai",
   "province": "Lumbini",
   "holdings": 80744,
   "parcels": 2.2,
   "irrigation": 0.867,
   "insufficiency": 0.346,
   "severe": 0.05,
   "rank": 76
  },
  {
   "name": "Bhaktapur",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 25983,
   "parcels": 2.7,
   "irrigation": 0.488,
   "insufficiency": 0.635,
   "severe": 0.081,
   "rank": 41
  },
  {
   "name": "Bhojpur",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 34784,
   "parcels": 2.5,
   "irrigation": 0.268,
   "insufficiency": 0.728,
   "severe": 0.026,
   "rank": 22
  },
  {
   "name": "Chitwan",
   "belt": "Terai",
   "province": "Bagmati",
   "holdings": 89519,
   "parcels": 1.8,
   "irrigation": 0.716,
   "insufficiency": 0.424,
   "severe": 0.074,
   "rank": 68
  },
  {
   "name": "Dadeldhura",
   "belt": "Hill",
   "province": "Sudurpashchim",
   "holdings": 26984,
   "parcels": 3.4,
   "irrigation": 0.323,
   "insufficiency": 0.758,
   "severe": 0.047,
   "rank": 16
  },
  {
   "name": "Dailekh",
   "belt": "Hill",
   "province": "Karnali",
   "holdings": 49646,
   "parcels": 2.7,
   "irrigation": 0.308,
   "insufficiency": 0.788,
   "severe": 0.028,
   "rank": 10
  },
  {
   "name": "Dang",
   "belt": "Terai",
   "province": "Lumbini",
   "holdings": 101880,
   "parcels": 2.3,
   "irrigation": 0.683,
   "insufficiency": 0.492,
   "severe": 0.062,
   "rank": 55
  },
  {
   "name": "Darchula",
   "belt": "Mountain",
   "province": "Sudurpashchim",
   "holdings": 24930,
   "parcels": 3.5,
   "irrigation": 0.178,
   "insufficiency": 0.782,
   "severe": 0.028,
   "rank": 11
  },
  {
   "name": "Dhading",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 68780,
   "parcels": 3.0,
   "irrigation": 0.312,
   "insufficiency": 0.636,
   "severe": 0.038,
   "rank": 40
  },
  {
   "name": "Dhankuta",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 31526,
   "parcels": 2.3,
   "irrigation": 0.27,
   "insufficiency": 0.64,
   "severe": 0.025,
   "rank": 38
  },
  {
   "name": "Dhanusha",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 105255,
   "parcels": 3.4,
   "irrigation": 0.723,
   "insufficiency": 0.473,
   "severe": 0.044,
   "rank": 56
  },
  {
   "name": "Dolakha",
   "belt": "Mountain",
   "province": "Bagmati",
   "holdings": 40894,
   "parcels": 3.8,
   "irrigation": 0.255,
   "insufficiency": 0.672,
   "severe": 0.019,
   "rank": 32
  },
  {
   "name": "Dolpa",
   "belt": "Mountain",
   "province": "Karnali",
   "holdings": 8373,
   "parcels": 3.7,
   "irrigation": 0.266,
   "insufficiency": 0.869,
   "severe": 0.001,
   "rank": 1
  },
  {
   "name": "Doti",
   "belt": "Hill",
   "province": "Sudurpashchim",
   "holdings": 39572,
   "parcels": 3.5,
   "irrigation": 0.382,
   "insufficiency": 0.77,
   "severe": 0.019,
   "rank": 13
  },
  {
   "name": "Gorkha",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 60028,
   "parcels": 3.3,
   "irrigation": 0.273,
   "insufficiency": 0.692,
   "severe": 0.037,
   "rank": 28
  },
  {
   "name": "Gulmi",
   "belt": "Hill",
   "province": "Lumbini",
   "holdings": 55911,
   "parcels": 3.1,
   "irrigation": 0.146,
   "insufficiency": 0.815,
   "severe": 0.04,
   "rank": 8
  },
  {
   "name": "Humla",
   "belt": "Mountain",
   "province": "Karnali",
   "holdings": 9707,
   "parcels": 6.3,
   "irrigation": 0.121,
   "insufficiency": 0.731,
   "severe": 0.002,
   "rank": 21
  },
  {
   "name": "Ilam",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 61874,
   "parcels": 1.9,
   "irrigation": 0.33,
   "insufficiency": 0.662,
   "severe": 0.047,
   "rank": 34
  },
  {
   "name": "Jajarkot",
   "belt": "Hill",
   "province": "Karnali",
   "holdings": 33431,
   "parcels": 3.7,
   "irrigation": 0.146,
   "insufficiency": 0.693,
   "severe": 0.008,
   "rank": 27
  },
  {
   "name": "Jhapa",
   "belt": "Terai",
   "province": "Koshi",
   "holdings": 148133,
   "parcels": 1.7,
   "irrigation": 0.719,
   "insufficiency": 0.463,
   "severe": 0.129,
   "rank": 59
  },
  {
   "name": "Jumla",
   "belt": "Mountain",
   "province": "Karnali",
   "holdings": 21548,
   "parcels": 6.2,
   "irrigation": 0.224,
   "insufficiency": 0.651,
   "severe": 0.006,
   "rank": 36
  },
  {
   "name": "Kailali",
   "belt": "Terai",
   "province": "Sudurpashchim",
   "holdings": 127016,
   "parcels": 2.4,
   "irrigation": 0.877,
   "insufficiency": 0.399,
   "severe": 0.063,
   "rank": 70
  },
  {
   "name": "Kalikot",
   "belt": "Mountain",
   "province": "Karnali",
   "holdings": 24432,
   "parcels": 4.1,
   "irrigation": 0.416,
   "insufficiency": 0.793,
   "severe": 0.031,
   "rank": 9
  },
  {
   "name": "Kanchanpur",
   "belt": "Terai",
   "province": "Sudurpashchim",
   "holdings": 86170,
   "parcels": 1.9,
   "irrigation": 0.892,
   "insufficiency": 0.365,
   "severe": 0.061,
   "rank": 73
  },
  {
   "name": "Kapilvastu",
   "belt": "Terai",
   "province": "Lumbini",
   "holdings": 84675,
   "parcels": 3.9,
   "irrigation": 0.668,
   "insufficiency": 0.413,
   "severe": 0.024,
   "rank": 69
  },
  {
   "name": "Kaski",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 53228,
   "parcels": 2.2,
   "irrigation": 0.538,
   "insufficiency": 0.609,
   "severe": 0.163,
   "rank": 44
  },
  {
   "name": "Kathmandu",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 50857,
   "parcels": 1.7,
   "irrigation": 0.494,
   "insufficiency": 0.676,
   "severe": 0.161,
   "rank": 30
  },
  {
   "name": "Kavrepalanchok",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 69941,
   "parcels": 2.8,
   "irrigation": 0.218,
   "insufficiency": 0.499,
   "severe": 0.032,
   "rank": 53
  },
  {
   "name": "Khotang",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 38131,
   "parcels": 3.0,
   "irrigation": 0.279,
   "insufficiency": 0.672,
   "severe": 0.007,
   "rank": 33
  },
  {
   "name": "Lalitpur",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 29991,
   "parcels": 1.5,
   "irrigation": 0.462,
   "insufficiency": 0.64,
   "severe": 0.048,
   "rank": 39
  },
  {
   "name": "Lamjung",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 31912,
   "parcels": 2.9,
   "irrigation": 0.498,
   "insufficiency": 0.556,
   "severe": 0.035,
   "rank": 49
  },
  {
   "name": "Mahottari",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 87062,
   "parcels": 2.8,
   "irrigation": 0.572,
   "insufficiency": 0.469,
   "severe": 0.048,
   "rank": 57
  },
  {
   "name": "Makawanpur",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 67523,
   "parcels": 1.8,
   "irrigation": 0.282,
   "insufficiency": 0.434,
   "severe": 0.013,
   "rank": 66
  },
  {
   "name": "Manang",
   "belt": "Mountain",
   "province": "Gandaki",
   "holdings": 951,
   "parcels": 5.7,
   "irrigation": 0.186,
   "insufficiency": 0.866,
   "severe": 0.013,
   "rank": 2
  },
  {
   "name": "Morang",
   "belt": "Terai",
   "province": "Koshi",
   "holdings": 145318,
   "parcels": 2.0,
   "irrigation": 0.828,
   "insufficiency": 0.442,
   "severe": 0.095,
   "rank": 64
  },
  {
   "name": "Mugu",
   "belt": "Mountain",
   "province": "Karnali",
   "holdings": 10929,
   "parcels": 6.1,
   "irrigation": 0.167,
   "insufficiency": 0.716,
   "severe": 0.008,
   "rank": 25
  },
  {
   "name": "Mustang",
   "belt": "Mountain",
   "province": "Gandaki",
   "holdings": 2366,
   "parcels": 3.9,
   "irrigation": 0.749,
   "insufficiency": 0.497,
   "severe": 0.015,
   "rank": 54
  },
  {
   "name": "Myagdi",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 21792,
   "parcels": 2.9,
   "irrigation": 0.252,
   "insufficiency": 0.705,
   "severe": 0.022,
   "rank": 26
  },
  {
   "name": "Nawalparasi East",
   "belt": "Terai",
   "province": "Gandaki",
   "holdings": 55412,
   "parcels": 2.1,
   "irrigation": 0.651,
   "insufficiency": 0.506,
   "severe": 0.072,
   "rank": 52
  },
  {
   "name": "Nawalparasi West",
   "belt": "Terai",
   "province": "Lumbini",
   "holdings": 55098,
   "parcels": 2.9,
   "irrigation": 0.768,
   "insufficiency": 0.352,
   "severe": 0.041,
   "rank": 74
  },
  {
   "name": "Nuwakot",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 56915,
   "parcels": 2.8,
   "irrigation": 0.467,
   "insufficiency": 0.457,
   "severe": 0.027,
   "rank": 61
  },
  {
   "name": "Okhaldhunga",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 32408,
   "parcels": 3.1,
   "irrigation": 0.157,
   "insufficiency": 0.757,
   "severe": 0.012,
   "rank": 17
  },
  {
   "name": "Palpa",
   "belt": "Hill",
   "province": "Lumbini",
   "holdings": 49742,
   "parcels": 3.2,
   "irrigation": 0.253,
   "insufficiency": 0.468,
   "severe": 0.003,
   "rank": 58
  },
  {
   "name": "Panchthar",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 36718,
   "parcels": 2.3,
   "irrigation": 0.221,
   "insufficiency": 0.762,
   "severe": 0.046,
   "rank": 15
  },
  {
   "name": "Parbat",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 25999,
   "parcels": 4.0,
   "irrigation": 0.476,
   "insufficiency": 0.586,
   "severe": 0.027,
   "rank": 46
  },
  {
   "name": "Parsa",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 60217,
   "parcels": 2.7,
   "irrigation": 0.883,
   "insufficiency": 0.351,
   "severe": 0.023,
   "rank": 75
  },
  {
   "name": "Pyuthan",
   "belt": "Hill",
   "province": "Lumbini",
   "holdings": 50717,
   "parcels": 2.9,
   "irrigation": 0.23,
   "insufficiency": 0.835,
   "severe": 0.057,
   "rank": 5
  },
  {
   "name": "Ramechhap",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 41863,
   "parcels": 3.2,
   "irrigation": 0.149,
   "insufficiency": 0.755,
   "severe": 0.019,
   "rank": 19
  },
  {
   "name": "Rasuwa",
   "belt": "Mountain",
   "province": "Bagmati",
   "holdings": 9312,
   "parcels": 3.6,
   "irrigation": 0.209,
   "insufficiency": 0.72,
   "severe": 0.021,
   "rank": 24
  },
  {
   "name": "Rautahat",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 86835,
   "parcels": 2.7,
   "irrigation": 0.885,
   "insufficiency": 0.456,
   "severe": 0.032,
   "rank": 62
  },
  {
   "name": "Rolpa",
   "belt": "Hill",
   "province": "Lumbini",
   "holdings": 46842,
   "parcels": 3.3,
   "irrigation": 0.107,
   "insufficiency": 0.765,
   "severe": 0.011,
   "rank": 14
  },
  {
   "name": "Rukum East",
   "belt": "Hill",
   "province": "Lumbini",
   "holdings": 11845,
   "parcels": 4.6,
   "irrigation": 0.029,
   "insufficiency": 0.629,
   "severe": 0.004,
   "rank": 42
  },
  {
   "name": "Rukum West",
   "belt": "Hill",
   "province": "Karnali",
   "holdings": 32773,
   "parcels": 2.9,
   "irrigation": 0.168,
   "insufficiency": 0.726,
   "severe": 0.009,
   "rank": 23
  },
  {
   "name": "Rupandehi",
   "belt": "Terai",
   "province": "Lumbini",
   "holdings": 117333,
   "parcels": 3.1,
   "irrigation": 0.851,
   "insufficiency": 0.319,
   "severe": 0.035,
   "rank": 77
  },
  {
   "name": "Salyan",
   "belt": "Hill",
   "province": "Karnali",
   "holdings": 49274,
   "parcels": 2.8,
   "irrigation": 0.268,
   "insufficiency": 0.676,
   "severe": 0.019,
   "rank": 31
  },
  {
   "name": "Sankhuwasabha",
   "belt": "Mountain",
   "province": "Koshi",
   "holdings": 32372,
   "parcels": 2.9,
   "irrigation": 0.309,
   "insufficiency": 0.662,
   "severe": 0.021,
   "rank": 35
  },
  {
   "name": "Saptari",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 104660,
   "parcels": 3.3,
   "irrigation": 0.669,
   "insufficiency": 0.397,
   "severe": 0.038,
   "rank": 71
  },
  {
   "name": "Sarlahi",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 105230,
   "parcels": 2.5,
   "irrigation": 0.71,
   "insufficiency": 0.461,
   "severe": 0.058,
   "rank": 60
  },
  {
   "name": "Sindhuli",
   "belt": "Hill",
   "province": "Bagmati",
   "holdings": 54735,
   "parcels": 2.3,
   "irrigation": 0.455,
   "insufficiency": 0.515,
   "severe": 0.041,
   "rank": 51
  },
  {
   "name": "Sindhupalchok",
   "belt": "Mountain",
   "province": "Bagmati",
   "holdings": 61865,
   "parcels": 3.7,
   "irrigation": 0.334,
   "insufficiency": 0.612,
   "severe": 0.019,
   "rank": 43
  },
  {
   "name": "Siraha",
   "belt": "Terai",
   "province": "Madhesh",
   "holdings": 104943,
   "parcels": 3.4,
   "irrigation": 0.682,
   "insufficiency": 0.43,
   "severe": 0.045,
   "rank": 67
  },
  {
   "name": "Solukhumbu",
   "belt": "Mountain",
   "province": "Koshi",
   "holdings": 22797,
   "parcels": 3.4,
   "irrigation": 0.105,
   "insufficiency": 0.682,
   "severe": 0.006,
   "rank": 29
  },
  {
   "name": "Sunsari",
   "belt": "Terai",
   "province": "Koshi",
   "holdings": 97770,
   "parcels": 2.3,
   "irrigation": 0.842,
   "insufficiency": 0.448,
   "severe": 0.102,
   "rank": 63
  },
  {
   "name": "Surkhet",
   "belt": "Hill",
   "province": "Karnali",
   "holdings": 62526,
   "parcels": 2.1,
   "irrigation": 0.455,
   "insufficiency": 0.566,
   "severe": 0.035,
   "rank": 48
  },
  {
   "name": "Syangja",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 51592,
   "parcels": 4.1,
   "irrigation": 0.275,
   "insufficiency": 0.741,
   "severe": 0.055,
   "rank": 20
  },
  {
   "name": "Tanahu",
   "belt": "Hill",
   "province": "Gandaki",
   "holdings": 58595,
   "parcels": 2.6,
   "irrigation": 0.295,
   "insufficiency": 0.606,
   "severe": 0.081,
   "rank": 45
  },
  {
   "name": "Taplejung",
   "belt": "Mountain",
   "province": "Koshi",
   "holdings": 24032,
   "parcels": 2.1,
   "irrigation": 0.405,
   "insufficiency": 0.643,
   "severe": 0.02,
   "rank": 37
  },
  {
   "name": "Terhathum",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 18698,
   "parcels": 1.9,
   "irrigation": 0.34,
   "insufficiency": 0.552,
   "severe": 0.012,
   "rank": 50
  },
  {
   "name": "Udayapur",
   "belt": "Hill",
   "province": "Koshi",
   "holdings": 61546,
   "parcels": 2.1,
   "irrigation": 0.43,
   "insufficiency": 0.576,
   "severe": 0.052,
   "rank": 47
  }
 ]
};
