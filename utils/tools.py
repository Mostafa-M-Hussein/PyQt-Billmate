# import os
# import subprocess


# def convert_to_ts_files(files):
#     try:
#         files = "".join(["../views/" + text for text in files])
#         cmd = f"pylupdate5   {files} -ts ar.ts  -ts  en.ts  "
#         print(cmd)
#         subprocess.check_output(cmd, shell=True)
#     except Exception as e:
#         print(e)


# convert_to_ts_files(["main_window.py"])
