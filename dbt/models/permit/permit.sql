{{ config(
  materialized = 'view'
) }}

select
  p.permit_number,
  p.permit_link,
  p.master_permit_number,
  p.application_date,
  p.status_date,
  p.status,
  p.issued_date,
  p.expires_date,
  addr.id as permit_address_id
from
  {{ ref('permit_raw') }} as p
  inner join {{ ref('permit_address') }} as addr
  on addr.address = p.permit_address
  and p.permit_city = addr.city
  and p.permit_state = addr.state
  and p.permit_zip = addr.zipcode
