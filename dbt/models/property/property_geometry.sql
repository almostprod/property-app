{{ config(
    materialized = 'table'
) }}

select
    p.prop_id as property_id,
    p.geo_id as geo_id,
    p.gis_acres as acres,
    p.geometry
from
    {{ source(
        'tcad',
        "parcel"
    ) }} as p
where p.geo_id is not null
