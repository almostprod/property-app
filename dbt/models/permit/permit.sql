{{ config(
  materialized = 'view'
) }}

select
  p.permit_number,
  p.permit_tcad_id as geo_id,
  p.master_permit_number,
  p.application_date,
  p.status_date,
  p.status,
  p.issued_date,
  p.expires_date,
  p.permit_link as permit_url
from
  {{ ref('permit_raw') }} as p
