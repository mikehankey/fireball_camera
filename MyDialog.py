from tkinter import *

class MyDialog:
    def __init__(self, parent, mft):
        self.mft = mft 
        self.parent = parent
        top = self.top = Toplevel(parent)

    

        exists = 0
        #
        if self.mft.cal_time is None:
           cal_time = "YYYY-MM-DD HH:MM:SS" 
        else:
           exists = 1
           cal_time = str(self.mft.cal_time)
        Label(top, text="Calibration Time in UTC").pack()
        self.e1 = Entry(top, textvariable=cal_time)

        if exists == 1:
           self.e1.delete(0, 'end')
        self.e1.insert(0, cal_time)
        self.e1.pack(padx=5)

        exists = 0

        #
        if self.mft.obs_code is None:
           obs_code = ""
        else:
           exists = 1
           obs_code = str(self.mft.obs_code)
        Label(top, text="Observatory Code").pack()
        self.e2a = Entry(top, textvariable=obs_code)
        if exists == 1:
           self.e2a.delete(0, 'end')
        self.e2a.insert(0, obs_code)
        self.e2a.pack(padx=5)


        #
        if self.mft.loc_lat is None:
           lat = "XX.ZZ" 
        else:
           exists = 1
           lat = str(self.mft.loc_lat)
        Label(top, text="Latitude").pack()
        self.e2 = Entry(top, textvariable=lat)
        if exists == 1:
           self.e2.delete(0, 'end')
        self.e2.insert(0, lat)
        self.e2.pack(padx=5)

        exists = 0
        #
        if self.mft.loc_lon is None:
           lon = "YY.ZZ" 
        else:
           lon = str(self.mft.loc_lon)
           exists = 1
        Label(top, text="Longitude").pack()
        self.e3 = Entry(top, textvariable=lon)
        if exists == 1:
           self.e3.delete(0, 'end')
        self.e3.insert(0, lon)
        self.e3.pack(padx=5)

        exists = 0
        #
        if self.mft.loc_alt is None:
           alt = "ZZ.ZZ" 
        else:
           alt = str(self.mft.loc_alt)
           exists = 1
        Label(top, text="Altitude").pack()
        self.e4 = Entry(top, textvariable=alt)
        if exists == 1:
            self.e4.delete(0, 'end')
        self.e4.insert(0, alt)
        self.e4.pack(padx=5)

        exists = 0
        #
        if self.mft.fb_dt is None:
           fb_dt = "YYYY-MM-DD HH:MM:SS " 
        else:
           exists = 1
           fb_dt = str(self.mft.fb_dt)
        Label(top, text="Fireball Datetime").pack()
        self.e5 = Entry(top, textvariable=fb_dt)
        if exists == 1:
            self.e5.delete(0, 'end')
        self.e5.insert(0, fb_dt)
        self.e5.pack(padx=5)




 
      


        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)


    def result(self):
        value = str(self.e.get())
        return(value)

    def ok(self):

        self.mft.obs_code = self.e5.get()
        self.mft.cal_time = self.e1.get()
        self.mft.loc_lat = self.e2.get()
        self.mft.loc_lon = self.e3.get()
        self.mft.loc_alt = self.e4.get()
        self.mft.fb_dt = self.e5.get()
        print("CALTIME: ", self.mft.cal_time)
        print ("value is", self.e1.get())
        self.top.destroy()
