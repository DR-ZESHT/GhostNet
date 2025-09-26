import os
import time
import requests
import netifaces
from color import *

os.system("clear")

interface = netifaces.gateways()
defult_interface = interface["default"][2][1]

if os.geteuid() != 0:
    print(RED+"You need to run this script with sudo.")
    exit()

print(MAGENTA+ r"""
 _______  __   __  _______  _______  _______  __    _  _______  _______ 
|       ||  | |  ||       ||       ||       ||  |  | ||       ||       |
|    ___||  |_|  ||   _   ||  _____||_     _||   |_| ||    ___||_     _|
|   | __ |       ||  | |  || |_____   |   |  |       ||   |___   |   |  
|   ||  ||       ||  |_|  ||_____  |  |   |  |  _    ||    ___|  |   |  
|   |_| ||   _   ||       | _____| |  |   |  | | |   ||   |___   |   |  
|_______||__| |__||_______||_______|  |___|  |_|  |__||_______|  |___|
""")

def menu():

    print(RED+"""
[1] Change MAC ADDRESS
[2] connect to Tor
[3] check DNS and IP
[4] Disconnect
[5] exit
""")

def change_mac():
    if os.path.exists("/usr/bin/macchanger") == False:
        os.system("sudo ./mcdownload.sh")
    os.system(f"sudo ./mcchanger.sh {defult_interface}")
    print(GREEN + "change mac adress was succesfuly","\n")

def check_tor():
    tor_path = "/etc/tor/torrc"
    required_lines = [
        "VirtualAddrNetworkIPv4 10.192.0.0/10",
        "AutomapHostsOnResolve 1",
        "TransPort 9040 IsolateClientAddr IsolateClientProtocol IsolateDestAddr IsolateDestPort",
        "DNSPort 5353"
    ]

    with open(tor_path, "r") as f:
        existing_lines = f.read().splitlines()

    with open(tor_path, "a") as f:
        for line in required_lines:
            if line not in existing_lines:
                f.write(line + "\n")

    print(BLUE + "[*] Verifying Tor configuration...")
    verify_result = os.system("sudo tor --verify-config")
    if verify_result != 0:
        print(RED + "[!] Tor config is invalid. Aborting.")
        return

    print(GREEN + "[*] Restarting Tor...")
    os.system("sudo systemctl restart tor")

    time.sleep(0.3)
    print(GREEN + "[*] Setting up iptables rules...")

    if os.path.exists("/etc/nftables.conf") == False :
        print(RED + "Downloading nftables")
        os.system("sudo pacman -S nftables")
        check_leak()
    elif os.path.exists("/etc/nftables.conf") == True :
        os.system("cp nftables.conf /etc/")
        os.system("sudo systemctl restart nftables")
    print(GREEN+"[*]Set DNS")
    with open("/etc/resolv.conf","w") as tor_resolv :
        tor_resolv.write("nameserver 127.0.0.1")
    print(RED + "All TCP traffic is now transparently routed through Tor.")



def check_leak():
    time.sleep(0.5)
    try :
        ip_check = requests.get("https://check.torproject.org/").text
        ip_address = requests.get("https://api64.ipify.org/").text
    except requests.exceptions.ConnectionError as err :
        print(RED+"Lose request")
    if "This browser is configured to use Tor." in ip_check:
        print(GREEN+"connection seccessfuly")
        time.sleep(1)
    else :
        print("Connetcion Field")
    print(GREEN+f"Your ip : {ip_address}")
    

def reset():
    print(GREEN+"stoping")
    os.system("sudo nft flush ruleset")
    with open("/etc/resolv.conf","w") as resolv:
        resolv.write("nameserver 8.8.8.8\nnameserver 1.1.1.1")
    print(RED+"Done")
def main() :
    while True:
        menu()
        choice = input(BLUE + "[*] your choice : ")
        if choice == "1":
            change_mac()
        elif choice == "2":
            check_tor()
        elif choice == "3":
            check_leak()
        elif choice == "4":
            reset()
        elif choice == "5":
            print("exit...")
            break
        else:
            print("Undifiend select.")
if __name__ == "__main__":
    main()