import enum

import sqlalchemy as sa
import geoalchemy2 as geosa
from sqlalchemy_utils import URLType

from property_app.database.app_base import app_metadata
from property_app.database.types import Enum


@enum.unique
class LandType(enum.Enum):
    COMMERCIAL_CONVERSION = "COMMERCIAL RES CONVERSION"
    EXEMPT = "TOTALLY EXEMPT PROPERTY"
    DUPLEX = "DUPLEX"
    CONDO = "COMMERCIAL CONDO"
    SINGLE_FAMILY = "SINGLE FAMILY RESIDENCE"
    TELEPHONE = "UTILITY (TELEPHONE)"
    MULTIFAMILY = "MULTIFAMILY"
    INDUSTRIAL = "INDUSTRIAL MAJOR MANUFACTURING IMPROVED"
    ACREAGE_NON_AG = "ACREAGE (NON-AG)"
    SINGLE_FAMILY_MH = "SINGLE FAMILY RESIDENCE MH"
    AG = "AG 1-D"
    RAILROAD = "UTILITY (RAILROADS)"
    COMMERCIAL = "COMMERCIAL IMPROVED"
    FOUR_PLEX = "FOUR-PLEX"
    WATER = "UTILITY (WATER)"
    VACANT_LAND = "VACANT LAND/MISC DETAILS"
    ACREAGE_AG = "ACREAGE (AG) 1-D-1"
    TRI_PLEX = "TRI-PLEX"
    FARM_AND_RANCH_MH = "FARM AND RANCH IMPR MH"
    SINGLE_FAMILY_DETALS = "SINGLE FAMILY RESIDENCE DETAILS"
    ELECTRIC = "UTILITY (ELECTRIC)"
    RESIDENTIAL = "RESIDENTIAL INVENTORY"
    COMMERCIAL_BEST_USE = "HS COMMERCIAL HIGHEST & BEST USE"
    FARM_AND_RANCH_IMPROVEMENT = "FARM AND RANCH IMPR"
    GAS = "UTILITY (GAS)"


property_record = sa.Table(
    "property",
    app_metadata,
    sa.Column("property_id", sa.Text),
    sa.Column("geo_id", sa.Text),
    sa.Column("full_address", sa.Text),
    sa.Column("street_number", sa.Text),
    sa.Column("street", sa.Text),
    sa.Column("zipcode", sa.Text),
    sa.Column("land_type", Enum(LandType)),
    sa.Column("acres", sa.Float),
    sa.Column("market_value", sa.Float),
    sa.Column("appraised_value", sa.Float),
    sa.Column("assessed_value", sa.Float),
    sa.Column("homesite_value", sa.Float),
    sa.Column("non_homesite_value", sa.Float),
    sa.Column("land_value", sa.Text),
    sa.Column("legal_description", sa.Text),
    sa.Column("tcad_url", URLType),
)


property_geometry = sa.Table(
    "property_geometry",
    app_metadata,
    sa.Column("property_id", sa.Text),
    sa.Column("geo_id", sa.Text),
    sa.Column("acres", sa.Float),
    sa.Column("geometry", geosa.Geometry),
)
