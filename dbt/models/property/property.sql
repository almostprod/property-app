{{ config(
    materialized = 'table'
) }}

select
    DISTINCT
    p.prop_id as property_id,
    p.geo_id as geo_id,
    p.situs_address as full_address,
    p.situs_num as street_number,
    p.situs_street as street,
    p.situs_zip as zipcode,
    p.land_type_desc as land_type,
    p.tcad_acres as acres,
    p.market_value as market_value,
    p.appraised_val as appraised_value,
    p.assessed_val as assessed_value,
    p.imprv_homesite_val as homesite_value,
    p.imprv_non_homesite_val as non_homesite_value,
    p.land_non_homesite_val as land_value,
    p.legal_desc as legal_description,
    p.hyperlink as tcad_url
from
    {{ source(
        'tcad',
        "parcel"
    ) }} as p
where p.geo_id is not null
