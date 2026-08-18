Request payload models (`SourcePost`, `CandidatePost`, `PhotometryPost`,
`SpectrumPost`, `ClassificationPost`) now reject unknown fields instead of
silently ignoring them, so a typo'd field name raises a validation error.
Response models still keep unmodeled server fields as extra attributes.
