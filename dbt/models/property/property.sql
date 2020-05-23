{{ config(
    materialized = 'table'
) }}

select
    *
from
    {{ source(
        'tcad',
        "prop"
    ) }} as p
where
    calendar_year_issued >= '1980'
