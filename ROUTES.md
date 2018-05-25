### API

POST: `/data-listing`
```
{ }
```

POST: `/chromosomes`
```
{ }
```

POST: `/signature-genome-bins`
```
{
	"regionWidth": 5000000,
	"signatures": ["COSMIC 1", "COSMIC 3"],
	"sources": ["PCAWG-PRAD-UK"]
}
```

POST: `/exposures`
```
{
	"signatures": ["COSMIC 1", "COSMIC 3"],
	"sources": ["PCAWG-PRAD-UK"]
}
```

POST: `/kataegis`
```
{
	"sources": ["PCAWG-PRAD-UK"]
}
```

POST: `/kataegis-rainfall`
```
{
	"proj_id": "PCAWG-PRAD-UK",
	"donor_id": "DO51965"
}
```

POST: `/signatures`
```
{ }
```
