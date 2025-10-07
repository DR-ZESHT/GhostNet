import os
import subprocess
import re
import time
import curses
import requests
import netifaces
import shutil

# colors
from color import RED, GREEN, YELLOW, CYAN, RESET
from curses import wrapper

# get interface 
interface = netifaces.gateways()
defult_interface = interface["default"][2][1]

# بررسی دسترسی root
if os.geteuid() != 0:
    print(RED + "You need to run this script with sudo." + RESET)
    exit()

# DEVNULL road
DEVNULL = open(os.devnull, 'wb')

# =======================
# helpfull functions
# =======================

def center_text(stdscr, text, y=None, color_pair=None):
    """perint center text"""
    height, width = stdscr.getmaxyx()
    lines = text.splitlines()
    if y is None:
        y = (height - len(lines)) // 2
    for i, line in enumerate(lines):
        x = max(0, (width - len(line)) // 2)
        if color_pair:
            stdscr.attron(curses.color_pair(color_pair))
        stdscr.addstr(y + i, x, line)
        if color_pair:
            stdscr.attroff(curses.color_pair(color_pair))
    stdscr.refresh()

def type_effect(stdscr, text, y=None, color_pair=None, delay=0.02):
    """print text with efect"""
    height, width = stdscr.getmaxyx()
    if y is None:
        y = height // 2
    x = max(0, (width - len(text)) // 2)
    if color_pair:
        stdscr.attron(curses.color_pair(color_pair))
    for i, char in enumerate(text):
        stdscr.addstr(y, x + i, char)
        stdscr.refresh()
        time.sleep(delay)
    if color_pair:
        stdscr.attroff(curses.color_pair(color_pair))

# =======================
# menu & operators
# =======================

def menu(stdscr):
    stdscr.clear()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    logo = """
 _______  __   __  _______  _______  _______  __    _  _______  _______ 
|       ||  | |  ||       ||       ||       ||  |  | ||       ||       |
|    ___||  |_|  ||   _   ||  _____||_     _||   |_| ||    ___||_     _|
|   | __ |       ||  | |  || |_____   |   |  |       ||   |___   |   |  
|   ||  ||       ||  |_|  ||_____  |  |   |  |  _    ||    ___|  |   |  
|   |_| ||   _   ||       | _____| |  |   |  | | |   ||   |___   |   |  
|_______||__| |__||_______||_______|  |___|  |_|  |__||_______|  |___|
"""
    center_text(stdscr, logo, color_pair=1)

    menu_list = [
        "[1] Change MAC ADDRESS",
        "[2] Connect to Tor",
        "[3] Check DNS and IP",
        "[4] Disconnect",
        "[5] Exit"
    ]
    start_y = len(logo.splitlines()) + 2
    for i, line in enumerate(menu_list):
        center_text(stdscr, line, y=start_y + i, color_pair=2)

# =======================
# operators
# =======================

def change_mac(stdscr):
    stdscr.clear()
    type_effect(stdscr, "Changing MAC Address...", color_pair=2)
    stdscr.refresh()
    if os.path.exists("/usr/bin/macchanger") == False:
        os.system("sudo bash/mcdownload.sh")
    os.system("sudo ./bash/mcchanger.sh")
    type_effect(stdscr, "MAC Address changed successfully!", color_pair=2, y=(stdscr.getmaxyx()[0]//2)+2)
    stdscr.getch()

def check_tor(stdscr):
    stdscr.clear()
    type_effect(stdscr, "Connecting via Tor...", color_pair=2)
    tor_path = "/etc/tor/torrc"
    required_lines = [
        "VirtualAddrNetworkIPv4 10.192.0.0/10",
        "AutomapHostsOnResolve 1",
        "TransPort 9040 IsolateClientAddr IsolateClientProtocol IsolateDestAddr IsolateDestPort",
        "DNSPort 5353"
    ]
    # backup
    shutil.copy(tor_path, tor_path + ".bak")

    with open(tor_path, "r") as f:
        existing_lines = f.read().splitlines()

    with open(tor_path, "a") as f:
        for line in required_lines:
            if line not in existing_lines:
                f.write(line + "\n")

    os.system("sudo bash bash/restart.sh")
    if not os.path.exists("/etc/nftables.conf"):
        subprocess.run(["sudo", "pacman", "-S", "nftables"], stdout=DEVNULL, stderr=DEVNULL)
    else:
        subprocess.run(["sudo", "bash", "bash/torstart.sh"], stdout=DEVNULL, stderr=DEVNULL)

    if defult_interface != "wlan0":
        shutil.copy("nftables.conf", "nftables.conf.bak")
        with open("nftables.conf", "r") as f:
            content = f.read()
        content = re.sub("wlan0", defult_interface, content)
        with open("nftables.conf", "w") as f:
            f.write(content)

    shutil.copy("/etc/resolv.conf", "/etc/resolv.conf.bak")
    with open("/etc/resolv.conf", "w") as f:
        f.write("nameserver 127.0.0.1")

    type_effect(stdscr, "Tor setup completed!", color_pair=2, y=(stdscr.getmaxyx()[0]//2)+2)
    stdscr.getch()

def check_leak(stdscr):
    stdscr.clear()
    type_effect(stdscr, "Checking IP / DNS Leak...", color_pair=2)
    time.sleep(0.5)
    try:
        ip_check = requests.get("https://check.torproject.org/").text
        ip_address = requests.get("https://api64.ipify.org/").text
    except requests.exceptions.ConnectionError:
        type_effect(stdscr, "Connection failed!", color_pair=3, y=(stdscr.getmaxyx()[0]//2)+2)
        stdscr.getch()
        return

    if "This browser is configured to use Tor." in ip_check:
        type_effect(stdscr, f"Connection successful! IP: {ip_address}", color_pair=2, y=(stdscr.getmaxyx()[0]//2)+2)
    else:
        type_effect(stdscr, "Connection not successful", color_pair=3, y=(stdscr.getmaxyx()[0]//2)+2)
    stdscr.getch()

def reset_connection(stdscr):
    stdscr.clear()
    type_effect(stdscr, "Disconnecting...", color_pair=3)
    subprocess.run(["sudo", "nft", "flush", "ruleset"], stdout=DEVNULL, stderr=DEVNULL)
    with open("/etc/resolv.conf", "w") as f:
        f.write("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
    type_effect(stdscr, "Connection reset done!", color_pair=2, y=(stdscr.getmaxyx()[0]//2)+2)
    stdscr.getch()

# =======================
# main function 
# =======================

def main(stdscr):
    curses.curs_set(0)
    while True:
        menu(stdscr)
        key = stdscr.getch()
        if key == ord('1'):
            change_mac(stdscr)
        elif key == ord('2'):
            check_tor(stdscr)
        elif key == ord('3'):
            check_leak(stdscr)
        elif key == ord('4'):
            reset_connection(stdscr)
        elif key == ord('5'):
            break
        else:
            continue

# =======================
# run
# =======================
if __name__ == "__main__" :
    wrapper(main)