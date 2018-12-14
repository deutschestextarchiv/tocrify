# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import click

from tocrify import Mets
from tocrify import Hocr

@click.command()
@click.argument('mets', type=click.File('rb'))
@click.option('-o', '--out-dir', type=click.Path(exists=True), required=True, help="Directory for storing the updated OCR files")
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
    for logical in mets.get_logicals():
        physical = mets.get_first_physical_for_logical(logical)
        if physical is not None:
            hocr = Hocr.read("%s/%s" % (mwd, mets.get_hocr_for_physical(physical).file_name))
            if hocr:
                hocr.ingest_structure(logical)
            else:
                click.echo(mets.get_hocr_for_physical(physical).file_name, err=True)
            

if __name__ == '__main__':
    cli()
