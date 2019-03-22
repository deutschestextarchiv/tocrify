# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import click

from tocrify import Mets
from tocrify import Hocr

@click.command()
@click.argument('mets', type=click.File('rb'))
@click.option('-o', '--out-dir', type=click.Path(exists=True), required=True, help="Existing directory for storing the updated OCR files")
@click.option('-O', '--order-file', type=click.File('w'), help="Destination for file order information")
def cli(mets,out_dir,order_file):
    """ METS: Input METS XML """
    
    click.echo("%s" % out_dir, err=True)
    mwd = os.path.abspath(os.path.dirname(mets.name))

    #
    # read in METS
    mets = Mets.read(mets)

    #
    # iterate over all elements of the logical struct map
    hocr_file_hocr = {}   
    for logical in mets.get_logicals():
        physical = mets.get_first_physical_for_logical(logical)
        if physical is not None:
            path = "%s/%s" % (mwd, mets.get_hocr_for_physical(physical).file_name)
            if path not in hocr_file_hocr:
                hocr_file_hocr[path] = Hocr.read(path)
            ingested = hocr_file_hocr[path].ingest_structure(logical)

    #
    # fill the order file and print updated hOCR files
    for order in sorted(mets.file_order.keys()):
        file_hocr = mets.get_hocr_for_physical(mets.get_physical(mets.file_order[order]))
        path = "%s/%s" % (mwd, file_hocr.file_name)
        if path not in hocr_file_hocr:
            hocr = Hocr.read(path)
        else:
            hocr = hocr_file_hocr[path]
        out_filename = "%s/%s" % (out_dir, os.path.basename(file_hocr.file_name))
        if order_file:
            order_file.write("%s\n" % out_filename)
        out_file = open(out_filename, "wb")
        hocr.write(out_file)
            

if __name__ == '__main__':
    cli()
