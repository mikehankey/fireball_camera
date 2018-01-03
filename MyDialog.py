import tkinter as tk
class MyDialog:



    def __init__(self, parent, cal_time, loc_lat, loc_lon, loc_alt, fb_time, title, label1text = '', label2text = '', label3text = '', label4text = '' , label5text = ''):

        print ("MD INIT!")
        self.cal_time = cal_time 
        self.loc_lat = loc_lat 
        self.loc_lon = loc_lon
        self.loc_alt = loc_alt
        self.fb_time = fb_time
 
        self.top = tk.Toplevel(parent)
        #self.top.transient(parent)
        #self.top.grab_set()
        if len(title) > 0: self.top.title(title)

        fields = ("Calibration Time", "Location Latitude", "Location Longitude", "Location Altitude", "Fireball Time")
        values= (self.cal_time, self.loc_lat, self.loc_lon, self.loc_alt, self.fb_time)
        self.entries = self.make_form(self.top, fields, values)

        #self.e.bind("<Return>", self.ok)
        #self.e.bind("<Escape>", self.cancel)
        #self.e.focus_set()

        b = tk.Button(self.top, text="OK", command=self.ok)
        b.pack(pady=5)

    def make_form(self, root, fields,values):
       self.entries = []
       x = 0
       for field in fields:
          row = tk.Frame(root)
          lab = tk.Label(row, width=15, text=field, anchor='w')
          ent = tk.Entry(row)
          value = tk.StringVar()
          value.set(values[x])
 
          ent.insert(0, value)
          row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
          lab.pack(side=tk.LEFT)
          ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
          self.entries.append((field, ent)) 
          x = x + 1
       return self.entries 
 
    def ok(self, event=None):
       for entry in self.entries:
           field = entry[0]
           text  = entry[1].get()
           if field == "Calibration Time":
              self.top.cal_time = text
           print('%s: "%s"' % (field, text)) 
       self.top.destroy()
 
    def cancel(self, event=None):
        self.top.destroy()
