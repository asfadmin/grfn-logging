import ems_report


def test_get_category():
    assert ems_report.get_category('foo-v1.png') \
           == 'SENTINEL-1_INTERFEROGRAMS_BROWSE'
    assert ems_report.get_category('foo-v1') \
           == 'SENTINEL-1_INTERFEROGRAMS'
    assert ems_report.get_category('S1-GUNW-A-R-018-tops-20230528_20230504-232801-00072W_00037S-PP-efd5-v2_0_6.png') \
           == 'SENTINEL-1_INTERFEROGRAMS_BROWSE'
    assert ems_report.get_category('S1-GUNW-A-R-018-tops-20230528_20230504-232801-00072W_00037S-PP-efd5-v2_0_6') \
           == 'SENTINEL-1_INTERFEROGRAMS'
    assert ems_report.get_category('S1-GUNW-A-R-091-tops-20240316_20240304-233600-00074W_00037S-PP-4b33-v3_0_1.png') \
           == 'ARIA_S1_GUNW_BROWSE'
    assert ems_report.get_category('S1-GUNW-A-R-091-tops-20240316_20240304-233600-00074W_00037S-PP-4b33-v3_0_1') \
           == 'ARIA_S1_GUNW'
    assert ems_report.get_category('foo-v4.png') \
           == 'ARIA_S1_GUNW_BROWSE'
    assert ems_report.get_category('foo-v4') \
           == 'ARIA_S1_GUNW'
