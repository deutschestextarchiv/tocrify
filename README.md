# tocrify
Pimp your OCR with structural information from METS.

## Background
OCR as delivered by commercial service providers (e.g. https://www.semantics.de/visual_library/) is
usually completely independent from costly collected structural data represented in METS files. This
tool aims at providing this missing connection. It is developed in the course of the DFG-funded project
[Digitale Sammlung Deutcher Kolonialismus](https://www.suub.uni-bremen.de/ueber-uns/projekte/dsdk/).

## Implementation
To create a mapping between the manually collected structural information in a METS file and the
corresponding OCR fulltext, the `<mets:structMap TYPE="LOGICAL" />` is evaluated. The labels of the
logical entities are mapped to the OCR fulltext using a moving window and Levenshtein distance as the
measure of confidence.

## Installation
Follows asap.

## Acknowledgements
The name of this tool was proposed by @kba. Parts of the code for METS handling was inspired by [metsrw](https://github.com/artefactual-labs/mets-reader-writer/).
