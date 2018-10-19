# -*- coding: utf-8 -*-
from __future__ import absolute_import

import click

from tocrify import Mets

@click.command()
@click.argument('mets', type=click.File('rb'))
@click.option('-o', '--out-dir', type=click.Path(exists=True), required=True, help="Directory for storing the updated OCR files")
@click.option('-O', '--order-file', type=click.File('w'), help="Destination for file order information")
def cli(mets,out_dir,order_file):
    """ METS: Input METS XML """
    
    click.echo("%s" % out_dir, err=True)

    #
    # read in METS
    mets = Mets.read(mets)

    #
    # iterate over all logical 
    for logical in mets.get_logicals():
        physical = mets.get_first_physical_for_logical(logical)
        if physical is not None:
            pass

if __name__ == '__main__':
    cli()
