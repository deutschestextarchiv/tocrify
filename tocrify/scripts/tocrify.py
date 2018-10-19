# -*- coding: utf-8 -*-
from __future__ import absolute_import

import click

@click.command()
@click.argument('mets', type=click.File('rb'))
@click.option('-o', '--out-dir', type=click.Path(exists=True), required=True, help="Directory for storing the updated OCR files")
@click.option('-O', '--order-file', type=click.File('w'), help="Destination for file order information")
def cli(mets,out_dir,order_file):
    """ METS: Input METS XML """
    
    click.echo("%s" % out_dir, err=True)

if __name__ == '__main__':
    cli()
