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
`tocrify` is implemented in Python 3. In the following, we assume a working Python 3
(tested versions 3.5 and 3.6) installation.

### virtualenv
Using [`virtualenv`](https://virtualenv.pypa.io/en/stable/) is highly recommended, although not strictly necessary for installing `tocrify`. It may be installed via:
```console
$ [sudo] pip install virtualenv
```
Create a virtual environement in a subdirectory of your choice (e.g. `env`) using
```console
$ virtualenv -p python3 env
```
and activate it.
```console
$ . env/bin/activate
```

### Python requirements
`tocrify` uses various 3rd party Python packages which may best be installed using `pip`:
```console
(env) $ pip install -r requirements.txt
```
Finally, `tocrify` itself can be installed via `pip`:
```console
(env) $ pip install .
```

## Acknowledgements
The name of this tool was proposed by @kba. Parts of the code for METS handling was inspired by [metsrw](https://github.com/artefactual-labs/mets-reader-writer/).
