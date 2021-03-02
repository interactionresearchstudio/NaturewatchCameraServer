import os
import subprocess

changedSettings = 0

# get SSID and passphrase from hostapd.conf
hostConfigFileName = "/etc/hostapd/hostapd.conf"
with open(hostConfigFileName, "r") as file:
    hostConfigFile = file.readlines()
currentSSID = hostConfigFile[2][5:].strip()
#currentPassphrase = hostConfigFile[10][15:].strip()
print("hostapd configuration - SSID: " + currentSSID)
#print("hostapd configuration - Passphrase: " + currentPassphrase)

# get SSID and passphrase from user configuration file
#nwConfigFileName = "/boot/_naturewatch-configuration.txt"
#with open(nwConfigFileName, "r") as file:
#    nwConfigFile = file.readlines()
#configFileSSID = nwConfigFile[1].strip()
#configFilePassphrase = nwConfigFile[3].strip()
#if "myNatureWatchCam" in configFileSSID :
unique_id = subprocess.check_output("sed -n 's/^Serial\s*: 0*//p' /proc/cpuinfo", shell=True)
configFileSSID = "MyNaturewatch-" + unique_id.strip().decode('utf-8')
print("Wifi Updated to unique name")

#print("Boot configuration - SSID: " + configFileSSID)
#print("Boot configuration - Passphrase: " + configFilePassphrase)

if configFileSSID == currentSSID:
    print("Config file and hostapd SSIDs match. No need to change them.")
else:
    hostConfigFile[2] = "ssid=" + configFileSSID + "\n"
    print("Updating hostapd config with new SSID...")
    changedSettings = 1

#if configFilePassphrase == currentPassphrase:
#    print("Config file and hostapd passphrases match. No need to change them.")
#else:
#    hostConfigFile[10] = "wpa_passphrase=" + configFilePassphrase + "\n"
#    print("Updating hostapd config with new passphrase...")
#    changedSettings = 1

#if os.path.isfile("/home/pi/firstboot"):
#    os.system("rm /home/pi/firstboot")
#    os.system("sudo raspi-config --expand-rootfs")
#    changedSettings = 1

if changedSettings == 1:
    with open(hostConfigFileName, "w") as file:
        file.writelines(hostConfigFile)
    print("Updated hostapd.conf.")
    os.system("sudo reboot now")
