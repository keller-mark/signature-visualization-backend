FORMAT: 1A

# ExploSig Server API
Note that this API does _not_ follow the traditional RESTful HTTP verb conventions. All requests are made via `POST`.

Table of Contents:
- [Data Listing](#data-listing-data-listing)
- [Signature](#signature-signature)
- [Exposures](#exposures-exposures)
- [Exposures - Single Sample](#exposures---single-sample-exposures-single-sample)
- [Kataegis](#kataegis-kataegis)
- [Rainfall](#rainfall-kataegis-rainfall)
- [Signature Genome Bins - Single Sample](#signature-genome-bins---single-sample-signature-genome-bins-single-sample)
- [Samples with Signatures](#samples-with-signatures-samples-with-signatures)
- [Hierarchical Clustering](#hierarchical-clustering-clustering)


## Data Listing [/data-listing]

+ Response 200 (application/json)

    + Body

            {
				"projects": [
					{

					},
					...
				],
				"signatures": [
					{

					},
					...
				],
				"cancer_type_map": [
					{

					},
					...
				],
				"tissue_types": [
					{
						
					},
					...
				]
			}


## Signature [/plot-signature]

+ Request (text/plain)

	+ Body

			{
				"signature": "COSMIC 1",
				"mut_type": "SBS"
			}

+ Response 200 (application/json)

	+ Body

			[
				{
					"cat_SBS": "A[C>A]A",
					"probability": 0.011098326
				},
				...
			]


## Exposures [/plot-exposures]

+ Request (text/plain)

	+ Body

			{
				"projects": [
					"TCGA-BRCA_BRCA_mc3.v0.2.8.WXS",
					...
				],
				"signatures": [
					"COSMIC 1",
					"COSMIC 2",
					...
				],
				"mut_type": "SBS",
				"tricounts_method": "None"
			}

+ Response 200 (application/json)

	+ Body

			[
				{
					"sample_id": "TCGA-BRCA_BRCA_mc3.v0.2.8.WXS TCGA-AN-A046-01A-21W-A050-09",
					"COSMIC 1": 108.97955986816488,
					"COSMIC 2": 4.50998877,
					...
				},
				...
			]


## Exposures - Single Sample [/plot-exposures-single-sample]

+ Request (text/plain)

	+ Body

			{
				"sample_id": "TCGA-BRCA_BRCA_mc3.v0.2.8.WXS TCGA-AN-A046-01A-21W-A050-09", 
				"projects": [
					"TCGA-BRCA_BRCA_mc3.v0.2.8.WXS",
					...
				], 
				"signatures": [
					"COSMIC 1",
					"COSMIC 2",
					...
				],
				"mut_type": "SBS",
				"tricounts_method": "None"
			}

+ Response 200 (application/json)

	+ Body

			[
				{
					"sig_SBS": "COSMIC 1",
					"exp_SBS_TCGA-BRCA_BRCA_mc3.v0.2.8.WXS TCGA-AN-A046-01A-21W-A050-09": 108.97955986816336
				},
				{
					"sig_SBS": "COSMIC 2",
					"exp_SBS_TCGA-BRCA_BRCA_mc3.v0.2.8.WXS TCGA-AN-A046-01A-21W-A050-09": 4.5099988998
				},
				...
			]


## Hierarchical Clustering [/clustering]

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
				},
				"tricounts_method": "None"
			}

+ Response 200 (application/json)

	+ Body

			{
				"children": [
					{
						"children": [
							{
								"children": [
									{
										"children": [
											{
												"children": [
													{
														"children": [
															{
																"children": [
																	{
																		"children": [],
																		"name": "SA569469"
																	},
																	{
																		"children": [],
																		"name": "SA570293"
																	}
																],
																"name": "SA569469-SA570293"
															},
															{
																"children": [
																	{
																		"children": [
																			{
																				"children": [
																					{
																						"children": [],
																						"name": "SA569588"
																					},
																					{
																						"children": [],
																						"name": "SA570579"
																					}
																				],
																				"name": "SA569588-SA570579"
																			},
																			...
																	},
																	...
															},
															...
													},
													...
											},
											...
									},
									...
							},
							...
					},
					...
			}