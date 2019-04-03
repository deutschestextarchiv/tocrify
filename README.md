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

### Clone the repository
The first installation step is the cloning of the repository:
```console
$ git clone https://github.com/deutschestextarchiv/tocrify.git
$ cd tocrify
```

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

### Python development library
`tocrify` depends on [`python-Levenshtein`](https://github.com/ztane/python-Levenshtein). To build it you may have to install the Python development library.

E.g., on apt-based linux:
```console
$ sudo apt install libpython3-dev
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

## Invocation
`tocrify` comes with a help message explaining its usage:
```console
(env) $ tocrify --help
Usage: tocrify [OPTIONS] METS

  METS: Input METS XML

Options:
  -o, --out-dir PATH         Existing directory for storing the updated OCR
                             files [required]
  -O, --order-file FILENAME  Destination for file order information
  -m, --mapping FILENAME     METS to hOCR structural types mapping
  --help                     Show this message and exit.
```
The METS file bundles all information on `tocrify`'s input, namely the `hOCR` files which have to be referenced in dedicated file groups (`fileGrp[@USE='FULLTEXT HOCR']`). With the help of the parameter `-o`, the output directory for the updated `hOCR` files can be specified. If given the parameter `-O`, `tocrify` writes the physical order of the `hOCR` files (which is not necessarily equal to their alphanumeric order) to the specified destination.

A sample invocation could look like:
```console
(env) $ tocrify -o hocr_plus -O order.txt export_mets_hocr.xml
```

## Acknowledgements
The name of this tool was proposed by @kba. Parts of the code for METS handling was inspired by [metsrw](https://github.com/artefactual-labs/mets-reader-writer/).
