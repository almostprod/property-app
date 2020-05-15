{{ config(
  materialized = 'view'
) }}

select
  permit_id
from
  {{ source(
    'permits_austin',
    "permits_austin"
  ) }}
