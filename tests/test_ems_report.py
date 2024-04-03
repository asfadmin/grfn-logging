import pytest

import ems_report


def test_get_category():
    assert ems_report.get_category('foo-v2_0_6.png') == 'SENTINEL-1_INTERFEROGRAMS_BROWSE'
    assert ems_report.get_category('foo-v2_0_6.unw_geo.zip') == \
           'SENTINEL-1_INSAR_UNWRAPPED_INTERFEROGRAM_AND_COHERENCE_MAP'
    assert ems_report.get_category('foo-v2_0_6') == 'SENTINEL-1_INTERFEROGRAMS'

    assert ems_report.get_category('foo-v3_0_1.png') == 'ARIA_S1_GUNW_BROWSE'
    assert ems_report.get_category('foo-v3_0_1') == 'ARIA_S1_GUNW'

    with pytest.raises(ValueError, match=r'^File foo must be v2_0_6 or v3_0_1$'):
        ems_report.get_category('foo')
