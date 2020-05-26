from __future__ import annotations

import pendulum

from datetime import datetime

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from pynamodb.attributes import (
    UnicodeAttribute,
    MapAttribute,
    ListAttribute,
    NumberAttribute,
    UTCDateTimeAttribute,
)

from pynamodb_attributes import IntegerAttribute

from property_app.config import get_config

config = get_config()


class PendulumDateTimeAttribute(UTCDateTimeAttribute):
    """
    An attribute for storing a `pendulum` datetime as a UTC string
    datetime is always stored as UTC but is deserialized in to a `pendulum`
    datetime.
    """

    def deserialize(self, value):
        """
        Takes a UTC datetime string and returns a pendulum object
        """
        dt = super(PendulumDateTimeAttribute, self).deserialize(value)

        return pendulum.instance(dt)


class BaseMeta:
    table_name = config.BASE_DDB_TABLE
    host = str(config.DDB_ENDPOINT)

    billing_mode = "PAY_PER_REQUEST"


class PropertyAppModel(Model):
    __model_prefix__ = None

    _primary_key = UnicodeAttribute(hash_key=True)
    _sort_key = UnicodeAttribute(range_key=True, null=True)

    created_at = PendulumDateTimeAttribute(default_for_new=datetime.utcnow)
    updated_at = PendulumDateTimeAttribute(default=datetime.utcnow)

    @classmethod
    def get_pk(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_sk(cls, *args, **kwargs):
        raise NotImplementedError


class AppraisalMap(MapAttribute):
    year = IntegerAttribute(null=True)
    market = IntegerAttribute(null=True)
    appraised = IntegerAttribute(null=True)
    homesite = IntegerAttribute(null=True)
    non_homesite = IntegerAttribute(null=True)
    land = IntegerAttribute(null=True)


class CoordinateMap(MapAttribute):
    lat = NumberAttribute()
    lon = NumberAttribute()


class Property(PropertyAppModel):
    __model_prefix__ = "Property"

    _type = UnicodeAttribute(default=__model_prefix__)

    property_id = UnicodeAttribute()
    tcad_url = UnicodeAttribute(null=True)

    appraisal = AppraisalMap(null=True)

    full_address = UnicodeAttribute(null=True)
    zipcode = UnicodeAttribute(null=True)
    coordinates = ListAttribute(of=CoordinateMap, null=True)

    geo_url = UnicodeAttribute(null=True)

    _zipcode_timestamp_id_sort = UnicodeAttribute(null=True)

    class PropertyZipcodeIndex(GlobalSecondaryIndex):
        class Meta:
            index_name = f"{config.BASE_DDB_TABLE}_PropertyZipcodeIndex"
            projection = AllProjection()

        zipcode = UnicodeAttribute(hash_key=True)
        _zipcode_timestamp_id_sort = UnicodeAttribute(range_key=True)

    zipcode_index = PropertyZipcodeIndex()

    class Meta(BaseMeta):
        index = []

    def __init__(self, property_id, **kwargs):
        hash_key = self.get_pk(property_id)
        range_key = self.get_sk(property_id)

        kwargs["property_id"] = property_id

        super(Property, self).__init__(hash_key=hash_key, range_key=range_key, **kwargs)

    @classmethod
    def get_pk(cls, property_id):
        return f"{cls.__model_prefix__}#{property_id}"

    @classmethod
    def get_sk(cls, property_id):
        return f"{cls.__model_prefix__}#{property_id}"

    def pre_persist_hook(self):
        timestamp = self.updated_at.isoformat()
        self._zipcode_timestamp_id_sort = f"{timestamp}-{self._primary_key}"
