import io
import zipfile
import logging

import click
import pandas as pd
import geopandas as gp

from .config import get_config
from .database import get_db


config = get_config()

log = logging.getLogger("parcel")

cli = click.Group(name="parcel", help="Texas Land Parcel ETL")

# Export source data with
# poetry run esri2geojson --jsonlines
# https://geo.traviscountytx.gov/arcgis/rest/services/TNR/TCAD/FeatureServer/0
# data/parcel/travis/travis.geojsonl


@cli.command("convert")
@click.option("--filename", type=str, required=True)
def convert_parcels(filename):
    db = get_db(schema="tcad")

    df = gp.read_file(filename)
    df.columns = [col.lower() for col in df.columns]

    df.dropna(subset=["geometry"], inplace=True)
    df.drop(columns=["objectid"], inplace=True)

    df.to_postgis(
        "parcel", db.engine, if_exists="replace", schema="tcad", chunksize=1000
    )
