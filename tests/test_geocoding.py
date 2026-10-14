import pytest
from app.core.geocoding import resolve_sector, TRICITY_SECTORS

def test_resolve_sector_explicit_chandigarh():
    res = resolve_sector("Pothole near sector 22 market")
    assert res["sector"] == "Sector 22"
    assert res["lat"] == 30.7300
    assert res["ward"] == 7

def test_resolve_sector_punjabi():
    res = resolve_sector("ਸਾਡੇ ਸੈਕਟਰ 35 ਵਿੱਚ ਸੜਕ ਖਰਾਬ ਹੈ")
    assert res["sector"] == "Sector 35"
    assert res["zone"] == "South-West"

def test_resolve_sector_hindi():
    res = resolve_sector("सेक्टर 15 में लाइटें बंद हैं")
    assert res["sector"] == "Sector 15"
    assert res["lat"] == 30.7510

def test_resolve_mohali_phase():
    res = resolve_sector("Heavy water logging in Phase 7 Mohali")
    assert res["sector"] == "Phase 7 Mohali"
    assert res["zone"] == "Mohali"

def test_resolve_panchkula_sector():
    res = resolve_sector("Broken street lights in sector 14 Panchkula")
    assert res["sector"] == "Sector 14 Panchkula"
    assert res["zone"] == "Panchkula"

def test_resolve_landmark():
    res = resolve_sector("Garbage dump outside Kiran Cinema")
    assert res["sector"] == "Sector 22"

def test_resolve_fallback():
    res = resolve_sector("General city problem without specific location")
    assert res["sector"] == "Sector 17"
