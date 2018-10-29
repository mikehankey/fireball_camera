star_file = "/mnt/ams2/cal/solved/20181002002140-1/20181002002140-1-star-dist-data.txt"

fp = open(star_file, 'r')
print("STAR_FILE", star_file)
for line in fp:
   exec(line)
fp.close()
print(star_dist_data)

