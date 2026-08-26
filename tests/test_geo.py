from dealfinder.geo import distance_miles

def test_same_point():
    assert distance_miles(51.0, 0.0, 51.0, 0.0) == 0

def test_london_to_dartford_reasonable():
    d = distance_miles(51.4462, 0.2169, 51.5074, -0.1278)
    assert 15 < d < 25
