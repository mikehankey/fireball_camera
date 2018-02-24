#!/usr/bin/python3
import dropbox
import sys

file_from = sys.argv[1]

parts = file_from.split('/')
file_to = "/" + parts[-1]

auth = "gVcpZxtO45QAAAAAAAAClg55t60ZVidTjkCmljxXhIsjjVmPgX_HhVqZ09M_cOM8"


def upload_file(file_from, file_to):
    dbx = dropbox.Dropbox(auth)
    f = open(file_from, 'rb')
    dbx.files_upload(f.read(), file_to)


upload_file(file_from,file_to)
