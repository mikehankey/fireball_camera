import subprocess 

# Restart the APP
sp = subprocess.Popen(['sudo','forever','restartall'])
sp.wait();
print('AMSCam Restarted');
