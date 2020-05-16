{{ config(
  materialized = 'view'
) }}

select
  permit_number as permit_number,
  permittype as permit_type,
  permit_class_mapped as permit_class,
  work_class as work_class,
  permit_location as permit_location,
  legal_description as permit_location_description,
  tcad_id as permit_tcad_id,
  applieddate :: DATE as application_date,
  issue_date :: DATE as issued_date,
  fiscal_year_issued as permit_fiscal_year,
  issue_method as issue_method,
  status_current as status,
  statusdate :: DATE as status_date,
  expiresdate :: DATE as expires_date,
  completed_date :: DATE as completed_date,
  original_address1 as permit_address,
  original_city as permit_city,
  original_state as permit_state,
  original_zip as permit_zip,
  council_district as council_district,
  link as permit_link,
  masterpermitnum as master_permit_number,
  latitude,
  longitude,
  contractor_trade,
  contractor_phone,
  contractor_address1,
  contractor_address2,
  contractor_city,
  contractor_zip,
  applicant_full_name,
  applicant_org,
  applicant_phone,
  applicant_address1,
  applicant_address2,
  applicant_city,
  applicantzip as applicant_zip,
  certificate_of_occupancy,
  total_lot_sq_ft
from
  {{ source(
    'permits_austin',
    "permits_austin_20200514"
  ) }} as p
where
  calendar_year_issued >= '1980'
