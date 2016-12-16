def read_config():
    config = {}
    file = open("config.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      config[data[0]] = data[1]
    return(config)


def read_sun():
    sun_info = {}
    file = open("sun.txt", "r")
    for line in file:
      line = line.strip('\n')
      data = line.rsplit("=",2)
      sun_info[data[0]] = data[1]
    return(sun_info)
