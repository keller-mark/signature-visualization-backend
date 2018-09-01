FORMAT: 1A

# iMuSE Server API
Note that this API does NOT follow the traditional RESTful HTTP verb conventions. All requests are made via `POST`.

Table of Contents:
- [Data Listing](#data-listing-data-listing)
- [Signature](#signature-signature)
- [Exposures](#exposures-exposures)
- [Exposures - Single Sample](#exposures---single-sample-exposures-single-sample)
- [Kataegis](#kataegis-kataegis)
- [Rainfall](#rainfall-kataegis-rainfall)
- [Signature Genome Bins](#signature-genome-bins-signature-genome-bins)
- [Signature Genome Bins - Single Sample](#signature-genome-bins---single-sample-signature-genome-bins-single-sample)

## Data Listing [/data-listing]

+ Response 200 (application/json)

    + Body

            {
				"projects": [
					{
						"id": "ICGC-BRCA-EU",
						"name": "Breast ER+ and HER2- Cancer - EU/UK",
						"num_donors": 569,
						"source": "ICGC",
						"has_clinical": true,
						"has_extended": true,
						"has_counts": true
					},
					...
				],
				"sigs": {
					"SBS": [
						{
							"name": "COSMIC 1",
							"description": "Signature 1 is the result...",
							"index": 10,
							"publication": "Alexandrov L.B. et al., Nature (2013)"
						},
						...
					],
					"DBS": [
						...
					],
					"INDEL": [
						...
					]
				},
				"sig_per_cancer_type": [
					{
						"group": "COSMIC",
						"id": "COSMIC",
						"cancer-types": [
							{
								"name": "Adrenocortical Carcinoma",
								"id": "COSMIC-ACC",
								"signatures": [
									"COSMIC 1",
									...
								]
							},
							...
						]
					},
					...
				]
			}


## Signature [/signature]

+ Request (text/plain)

	+ Body

			{
				"name": "COSMIC 1",
				"mut_type": "SBS"
			}

+ Response 200 (application/json)

	+ Body

			[
				{
					"sample_id": "SA543682",
					"proj_id": "ICGC-BRCA-EU",
					"exposures": {
						"SBS": {
							"COSMIC 1": 515.9603424981033,
							"COSMIC 2": 1.5975135739615894e-14,
							...
						},
						"DBS": {
							...
						},
						"INDEL": {
							...
						}
					},
					"clinical": {
						"Patient": "DO218489",
						"Tobacco User": "nan",
						"Diagnosis Age": 45,
						"Sex": "female",
						...
					}
				},
				...
			]


## Exposures [/exposures]

+ Request (text/plain)

	+ Body

			{
				"projects": [
					"ICGC-BRCA-EU",
					...
				],
				"signatures": {
					"SBS": [
						"COSMIC 1",
						...
					],
					"DBS": [
						...
					],
					"INDEL": [
						...
					]
				}
			}

+ Response 200 (application/json)

	+ Body

			[
				{
					"sample_id": "SA543682",
					"proj_id": "ICGC-BRCA-EU",
					"exposures": {
						"SBS": {
							"COSMIC 1": 515.9603424981033,
							"COSMIC 2": 1.5975135739615894e-14,
							...
						},
						"DBS": {
							...
						},
						"INDEL": {
							...
						}
					},
					"clinical": {
						"Patient": "DO218489",
						"Tobacco User": "nan",
						"Diagnosis Age": 45,
						"Sex": "female",
						...
					}
				},
				...
			]


## Exposures - Single Sample [/exposures-single-sample]

+ Request (text/plain)

	+ Body

			{
				"sample_id": "SA543682", 
				"proj_id": "ICGC-BRCA-EU", 
				"signatures": {
					"SBS": [
						"COSMIC 1",
						...
					],
					"DBS": [
						...
					],
					"INDEL": [
						...
					]
				}
			}

+ Response 200 (application/json)

	+ Body

			[
				{
					"sample_id": "SA543682",
					"proj_id": "ICGC-BRCA-EU",
					"exposures": {
						"SBS": {
							"COSMIC 7": 14.533149065470633,
							...
						},
						"DBS": {
							...
						},
						"INDEL": {
							...
						}
					},
					"clinical": {
						"Patient": "DO218489",
						"Tobacco User": "nan",
						"Diagnosis Age": 45,
						"Sex": "female",
						...
					}
				}
			]


## Kataegis [/kataegis]

+ Request (text/plain)

	+ Body

			{
				"projects": [
					"ICGC-BRCA-EU",
					...
				]
			}

+ Response 200 (application/json)

	+ Body

			{
				"SA543567": {
					"kataegis": {
						"8": [
							43624586,
							68097779
						],
						"10": [
							79959348,
							79959543
						],
						"12": [
							31335571
						],
						"15": [
							97354064
						],
						"16": [
							2398365
						],
						"17": [
							51822158,
							70629730,
							70629755
						],
						"20": [
							20690422,
							20690503,
							20690512,
							20690643
						]
					},
					"proj_id": "ICGC-BRCA-EU"
				},
				...
			}


## Rainfall [/kataegis-rainfall]

+ Request (text/plain)

	+ Body

			{
				"proj_id": "ICGC-BRCA-EU",
				"sample_id": "SA543567"
			}

+ Response 200 (text/csv)

	+ Body

			chr,pos,cat,mut_dist,kataegis
			1,1670458,A[C>A]A,1084547,0
			1,1930665,T[T>C]C,260207,0
			1,2057510,A[C>T]C,126845,0
			1,2110902,T[C>T]A,53392,0
			1,4136526,A[C>T]A,2025624,0
			1,4387515,A[T>G]A,250989,0
			1,4652247,T[C>T]G,264732,0


## Signature Genome Bins [/signature-genome-bins]

+ Request (text/plain)

	+ Body

			{
				"projects": ["PCAWG-BRCA-EU"],
				"signatures": {
					"SBS": [
						"COSMIC 1",
						...
					],
					"DBS": [
						...
					],
					"INDEL": [
						...
					]
				}, 
				"regionWidth": 1000000
			}

+ Response 200 (application/json)

	+ Body

		








