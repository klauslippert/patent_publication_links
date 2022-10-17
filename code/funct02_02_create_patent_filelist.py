import glob
files=glob.glob("/home/user/data/patent/*/*.xml")
for f in files:
    print(f)

