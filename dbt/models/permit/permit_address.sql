{{ config(
    materialized = 'table'
) }}

select
    md5(
        permit_address || permit_city || permit_state || permit_zip
    ) :: uuid as id,
    permit_address as address,
    permit_city as city,
    permit_state as state,
    permit_zip as zipcode,
    permit_tcad_id as tcad_id
from
    permit_raw
group by
    1,
    2,
    3,
    4,
    5,
    6
