- [ ] Proposed

An animal or belonging travelling with one person. `name` supplies the common
interoperable value. Producers may add item-specific attributes when useful;
consumers must preserve attributes they do not understand.

| Tag | Importance | Type | Description | Enum | Example |
|-----|------------|------|-------------|------|---------|
| name | required | string | Lowercase common name of the animal or belonging. Prefer an existing name where one is already in use. | | dog |

Examples:

```json
{"name": "dog"}
{"name": "guitar"}
{"name": "bicycle", "folding": true}
```

The first version deliberately standardizes only `name`. For example, dog
weight or bicycle dimensions should become shared optional fields only when
real producers need to exchange them; they need not be invented up front.
