
from view import log_motion_capture
from amscommon import read_config, caldate

values = {}
values['datetime'] = "2017-06-22 13:27:58"
values['motion_frames'] = 2
values['cons_motion'] = 2
values['color'] = 1
values['straight_line'] = 1
values['meteor_yn'] = 0
values['bp_frames'] = 3
log_motion_capture(read_config(), "./test_data/20170622132758.jpg", values)
