#/usr/bin/python3 

# wrapper for end-to-end calibration

# 1) run sense up and gather data ./sense-up.py sense_up
# 2) try to stack video into final image ./sense-up.py stack file
# 3) try to plate-solve the stacked image ./calibrate-image.py file
# 4) if calibration is successful upload calibration files
