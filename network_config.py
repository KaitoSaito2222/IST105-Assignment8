import sys
import re
import random
import time
import html

# Define constants
IPV4_SUBNET = "192.168.1.0/24"
IPV4_GATEWAY = "192.168.1.1"
IPV4_SUBNET_MASK = "255.255.255.0"
IPV6_SUBNET = "2001:db8::/64"
IPV6_GATEWAY = "2001:db8::1"
LEASE_TIME = 3600  # in seconds

# Format: {mac_address: {'ip': ip_address, 'expiry': timestamp}}
ip_leases = {}

def validate_mac_address(mac):
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))

def normalize_mac_address(mac):
    # Remove all separators and convert to uppercase
    mac_clean = re.sub(r'[^0-9A-Fa-f]', '', mac).upper()
    # Insert colons
    return ':'.join(mac_clean[i:i+2] for i in range(0, len(mac_clean), 2))

def eui64_ipv6_from_mac(mac):
    # Remove colons from MAC address
    mac_parts = mac.split(':')
    
    # Insert FF:FE in the middle of the MAC address
    eui64_parts = mac_parts[0:3] + ['FF', 'FE'] + mac_parts[3:6]
    
    # Convert first byte and flip the 7th bit (Universal/Local bit)
    first_byte = int(eui64_parts[0], 16)
    first_byte ^= 0x02  # Flip the 7th bit
    eui64_parts[0] = format(first_byte, '02X')
    
    # Create the IPv6 interface identifier
    interface_id = ''.join(eui64_parts)
    
    # Extract network prefix from IPV6_SUBNET (assuming it's in CIDR notation)
    prefix = IPV6_SUBNET.split('/')[0].rstrip(':')
    
    # Combine network prefix with interface ID to form the full IPv6 address
    ipv6_address = f"{prefix}::{interface_id[0:4]}:{interface_id[4:8]}:{interface_id[8:12]}:{interface_id[12:16]}"
    
    return ipv6_address

def allocate_ipv4(mac):
    current_time = time.time()
    
    # Check if there's an existing lease for this MAC
    if mac in ip_leases and 'ipv4' in ip_leases[mac]:
        lease = ip_leases[mac]
        if lease['expiry'] > current_time:
            # Existing lease is still valid
            return lease['ipv4']
        # Else lease expired, will allocate a new one
    
    # Available IP range (excluding network, gateway, and broadcast addresses)
    available_ips = [f"192.168.1.{i}" for i in range(2, 255)]
    
    # Remove IPs that are already leased and not expired
    for leased_mac, lease_info in ip_leases.items():
        if 'ipv4' in lease_info and lease_info['expiry'] > current_time:
            if lease_info['ipv4'] in available_ips:
                available_ips.remove(lease_info['ipv4'])
    
    if not available_ips:
        raise Exception("No available IPv4 addresses in the subnet")
    
    # Select a random available IP
    allocated_ip = random.choice(available_ips)
    
    # Update the lease
    ip_leases[mac] = {
        'ipv4': allocated_ip,
        'expiry': current_time + LEASE_TIME
    }
    
    return allocated_ip

def allocate_ipv6(mac):
    # Generate IPv6 address using EUI-64
    ipv6_address = eui64_ipv6_from_mac(mac)
    
    # Update the lease (IPv6 addresses don't expire in this simulation)
    if mac not in ip_leases:
        ip_leases[mac] = {}
    
    ip_leases[mac]['ipv6'] = ipv6_address
    ip_leases[mac]['expiry'] = time.time() + LEASE_TIME
    
    return ipv6_address

def generate_html_error(error_message):
    html_content = """<!DOCTYPE html>
<html>
<body>
    <h1>DHCP Configuration Error</h1>
    <p style="color: red;">{}</p>
</body>
</html>""".format(html.escape(error_message))
    return html_content

def generate_html_response(response_data, dhcp_version):
    """Generate simple HTML with just the required DHCP configuration results"""
    ip_field_name = "assigned_ipv4" if dhcp_version == "DHCPv4" else "assigned_ipv6"
    
    html_content = """<!DOCTYPE html>
<html>
<body>
  <p>mac_address: "{mac_address}"</p>
  <p>{ip_field_name}: "{assigned_ip}"</p>
  <p>lease_time: "{lease_time}"</p>
</body>
</html>""".format(
        mac_address=html.escape(response_data.get("mac_address", "")),
        ip_field_name=ip_field_name,
        assigned_ip=html.escape(response_data.get("assigned_ip", "")),
        lease_time=html.escape(response_data.get("lease_time", ""))
    )
    
    return html_content

def process_dhcp_request(mac_address, dhcp_version):
    """
    Process DHCP request and return appropriate HTML response.
    """
    # Validate MAC address
    if not mac_address:
        return generate_html_error("MAC address is required")
        
    if not validate_mac_address(mac_address):
        return generate_html_error("Invalid MAC address format. Please use format XX:XX:XX:XX:XX:XX")
    
    # Validate DHCP version
    if not dhcp_version or dhcp_version not in ["DHCPv4", "DHCPv6"]:
        return generate_html_error("Valid DHCP version (DHCPv4 or DHCPv6) is required")
    
    # Normalize MAC address
    mac_address = normalize_mac_address(mac_address)
    
    try:
        response = {
            "mac_address": mac_address,
            "lease_time": f"{LEASE_TIME} seconds"
        }
        
        if dhcp_version == "DHCPv4":
            ip = allocate_ipv4(mac_address)
            response["assigned_ip"] = ip
        else:  # DHCPv6
            ip = allocate_ipv6(mac_address)
            response["assigned_ip"] = ip
        
        return generate_html_response(response, dhcp_version)
    
    except Exception as e:
        return generate_html_error(str(e))

if __name__ == "__main__":
    if len(sys.argv) == 3:
        mac_address = sys.argv[1]
        dhcp_version = sys.argv[2]
        print(process_dhcp_request(mac_address, dhcp_version))
    else:
        print("<h1>Error</h1>")
        sys.exit(1)