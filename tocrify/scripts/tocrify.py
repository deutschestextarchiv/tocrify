# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import logging
import click

from pkg_resources import resource_filename, Requirement

from tocrify import Mets
from tocrify import Hocr
from tocrify import Mets2hocr

@click.command()
@click.argument('mets', type=click.File('rb'))
@click.option('-o', '--out-dir', type=click.Path(exists=True), required=True, help="Existing directory for storing the updated OCR files")
@click.option('-O', '--order-file', type=click.File('w'), help="Destination for file order information")
@click.option('-m', '--mapping', type=click.File('r'), default=os.path.realpath(resource_filename(Requirement.parse("tocrify"), 'tocrify/data/mets2hocr.yml')), help="METS to hOCR structural types mapping")
@click.option('-l', '--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARN', 'ERROR', 'OFF']), default='WARN')
@click.option('-b', '--backwards/--no-backwards', default=False, help="In cases of so-called 'ghost pages', search backwards for a non-ghost page (default: don't)")
def cli(mets,out_dir,order_file, mapping, log_level, backwards):
    """ METS: Input METS XML """
    
    mwd = os.path.abspath(os.path.dirname(mets.name))

    #
    # logging level
    logging.basicConfig(level=logging.getLevelName(log_level))

    #
    # read in METS
    mets = Mets.read(mets)

    #
    # read in METS-hOCR mapping
    mets2hocr = Mets2hocr.read(mapping)

    #
    # iterate over all elements of the logical struct map
    hocr_file_hocr = {}   
    for logical in mets.get_logicals():
        physical = mets.get_first_physical_for_logical(logical, backwards)
        if physical is not None:
            path = "%s/%s" % (mwd, mets.get_hocr_for_physical(physical).file_name)
            if path not in hocr_file_hocr:
                hocr_file_hocr[path] = Hocr.read(path, mets2hocr)
            ingested = hocr_file_hocr[path].ingest_structure(logical)

    #
    # fill the order file and print updated hOCR files
    for order in sorted(mets.file_order.keys()):
        file_hocr = mets.get_hocr_for_physical(mets.get_physical(mets.file_order[order]))
        path = "%s/%s" % (mwd, file_hocr.file_name)
        if path not in hocr_file_hocr:
            hocr = Hocr.read(path, mets2hocr)
        else:
            hocr = hocr_file_hocr[path]
        out_filename = "%s/%s" % (out_dir, os.path.basename(file_hocr.file_name))
        if order_file:
            order_file.write("%s\n" % out_filename)
        out_file = open(out_filename, "wb")
        hocr.write(out_file)
            

if __name__ == '__main__':
    cli()
