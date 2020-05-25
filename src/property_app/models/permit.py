import enum

import sqlalchemy as sa
from sqlalchemy_utils import URLType

from property_app.database.app_base import app_metadata
from property_app.database.types import Enum


@enum.unique
class PermitStatus(enum.Enum):
    CANCELLED = "Cancelled"
    PENDING = "Pending"
    PENDING_PERMIT = "Pending Permit"
    NEW_PERMIT_REQUIRED = "New Permit Required"
    WITHDRAWN = "Withdrawn"
    ABORTED = "Aborted"
    INACTIVE_CONTRACTOR = "Inactive Contractor"
    CANCELLED_CONTRACTOR = "Cancelled - Contractor Required"
    EXPIRED = "Expired"
    RE_REVIEW = "Re Review"
    ACTIVE = "Active"
    REJECTED = "Rejected"
    CANCELLED_NEW_PERMIT = "Cancelled - New Permit Required"
    INACTIVE_REVISION = "Inactive Pending Revision"
    SUSPENDED = "Suspended"
    VOID = "VOID"
    ON_HOLD = "On Hold"
    CLOSED = "Closed"
    REVOKED = "Revoked"
    FINAL = "Final"
    DENIED_CLOSED = "Denied but Closed"


building_permit = sa.Table(
    "permit",
    app_metadata,
    sa.Column("permit_number", sa.Text),
    sa.Column("geo_id", sa.Text),
    sa.Column("master_permit_number", sa.Numeric),
    sa.Column("status", Enum(PermitStatus)),
    sa.Column("status_date", sa.Date),
    sa.Column("application_date", sa.Date),
    sa.Column("issued_date", sa.Date),
    sa.Column("expires_date", sa.Date),
    sa.Column("permit_url", URLType),
)
