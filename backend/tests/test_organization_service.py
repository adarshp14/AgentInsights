import uuid
import re
import hashlib
from services.organization_service import OrganizationService


def test_create_org_collection_name_deterministic():
    service = OrganizationService(db=None)
    org_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    result1 = service.create_org_collection_name(org_id)
    result2 = service.create_org_collection_name(org_id)

    org_str = str(org_id).replace("-", "")
    expected_hash = hashlib.md5(org_str.encode()).hexdigest()[:8]
    expected = f"org_{expected_hash}_docs"

    assert result1 == expected
    assert result2 == expected
    assert re.fullmatch(r"org_[0-9a-f]{8}_docs", result1)
