import uuid
from datetime import datetime

from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    UTCDateTimeAttribute,
)


class AppProperty(Model):
    class Meta:
        table_name = "PropertyAppProperty"
        host = "http://localhost:8000"

    pk = UnicodeAttribute(hash_key=True)

    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)

    property_id = UnicodeAttribute(default=lambda: str(uuid.uuid4()))

    lat = NumberAttribute(null=True)
    lon = NumberAttribute(null=True)
