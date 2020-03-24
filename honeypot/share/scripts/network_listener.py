
from scapy.all import *

stop_sniffing = False
listen_ip = ''
def call_back(pkt):
    if IP in pkt and ICMP not in pkt:
        if pkt[IP].dst == listen_ip:
            global stop_sniffing
            stop_sniffing = True

def wait_for_activity(ip):
    global listen_ip
    listen_ip = ip
    sniff(iface="tap0", prn=call_back, stop_filter=lambda x: stop_sniffing)
