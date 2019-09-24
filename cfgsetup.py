import json
import os
import subprocess

changedSettings = 0

#if os.path.isfile("/home/pi/wificfg.json") == False:
#    os.system("wget https://raw.githubusercontent.com/interactionresearchstudio/NaturewatchCameraServer/wip/flask-server-AP/wificfg.json")

if os.path.isfile("/home/pi/firstboot") == False:
     fin = open("/boot/config.txt", "rt")
     data = fin.read()
     data = data.replace('start_x=0','start_x=1')
     fin.close()
     fin = open("/boot/config.txt","wt")
     fin.write(data)
     fin.close()
     with open("/home/pi/firstboot", 'a'):
         os.utime("/home/pi/firstboot", None)
     os.system("sudo raspi-config --expand-rootfs")
     changedSettings = 1
     os.system("sudo reboot now")

with open('/home/pi/NaturewatchCameraServer/wificfg.json','r') as json_file:
    cred_data = json.load(json_file)
    cred_ssid = cred_data["host_apd_cfg"]["ssid"]
    cred_pass = cred_data["host_apd_cfg"]["wpa_passphrase"]
    print(cred_ssid)
with open('/boot/_naturewatch-configuration.txt', 'r') as file:
    user_data = file.readlines()
    user_ssid = user_data[1].strip()
    user_pass = user_data[3].strip()
    print(user_ssid)	
if user_ssid == cred_ssid:
  print("user hasn't updated WiFi name")
  if "myNatureWatchCam" in user_ssid :
      unique_id = subprocess.check_output("sed -n 's/^Serial\s*: 0*//p' /proc/cpuinfo", shell=True)
      cred_data["host_apd_cfg"]["ssid"] = "myNatureWatchCam-" + unique_id.strip()
      changedSettings = 1
      print("Wifi Updated to unique name")
else:
  print("user has updated WiFi name")
  cred_data["host_apd_cfg"]["ssid"] = user_ssid
  print("SSID updated to " + user_ssid)
  changedSettings = 1

if user_pass == cred_pass:
  print("user hasn't updated WiFi password")
else:
  print("user has updated WiFi password")
  cred_data["host_apd_cfg"]["wpa_passphrase"] = user_pass
  print("Password updated to " + user_pass)
  changedSettings = 1

if changedSettings == 1:   
   with open("/home/pi/NaturewatchCameraServer/wificfg.json", "w") as jsonFile:
      json.dump(cred_data, jsonFile)
   print("saving file")


