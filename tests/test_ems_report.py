import ems_report


def test_get_category():
    assert ems_report.get_category('foo.png') == 'SENTINEL-1_INTERFEROGRAMS_BROWSE'
    assert ems_report.get_category('foo.unw_geo.zip') == 'SENTINEL-1_INSAR_UNWRAPPED_INTERFEROGRAM_AND_COHERENCE_MAP'
    assert ems_report.get_category('foo') == 'SENTINEL-1_INTERFEROGRAMS'
