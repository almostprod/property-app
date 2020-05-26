from property_app.models.property import property_record
from property_app.database.session import get_session

from property_app.crud import property as prop
from property_app import utility as u


def load_properties():
    db = get_session()

    records = (
        db.query(
            property_record.c.property_id,
            property_record.c.tcad_url,
            property_record.c.full_address,
            property_record.c.zipcode,
            property_record.c.market_value,
            property_record.c.land_value,
        )
        .order_by(property_record.c.property_id)
        .limit(10000)
        .yield_per(25)
    )

    for batch in u.batch(records.all(), 25):
        properties = []
        for record in batch:

            land_value = record.land_value
            if land_value is not None and isinstance(land_value, str):
                land_value = land_value.strip()
                land_value = "".join(c for c in land_value if c.isdigit())
                land_value = int(land_value) if land_value else None

            p = prop.create_property(
                record.property_id,
                tcad_url=record.tcad_url,
                full_address=record.full_address,
                zipcode=record.zipcode,
                market_value=record.market_value,
                land_value=land_value,
            )
            print(p)
            properties.append(p)

        prop.persist(properties)


