import typing as t

from datetime import datetime

from property_app.dynamodb import Property, AppraisalMap


def create_property(property_id: int, **kwargs) -> Property:

    appraisal = AppraisalMap()
    appraisal.year = 2019
    appraisal.market = kwargs.pop("market_value", None)
    appraisal.land = kwargs.pop("land_value", None)

    return Property(str(property_id), appraisal=appraisal, **kwargs)


def persist(properties: t.Union[Property, t.Iterable[Property]]) -> t.List[Property]:
    if isinstance(properties, Property):
        properties = [properties]

    with Property.batch_write() as batch:
        for property_record in properties:

            property_record.updated_at = datetime.utcnow()
            property_record.pre_persist_hook()
            batch.save(property_record)

    return properties


def find_by_id(property_ids: t.Union[int, t.List[int]], **kwargs) -> t.List[Property]:
    if not isinstance(property_ids, list):
        property_ids = [property_ids]

    keys = [(Property.get_pk(p_id), Property.get_sk(p_id)) for p_id in property_ids]

    return list(Property.batch_get(keys, **kwargs))


def find_by_zipcode(zipcodes: t.Union[str, t.List[str]], **kwargs) -> t.List[Property]:
    if not isinstance(zipcodes, list):
        zipcodes = [zipcodes]

    keys = [(Property.get_pk(p_id), Property.get_sk(p_id)) for p_id in zipcodes]

    return list(Property.batch_get(keys, **kwargs))
