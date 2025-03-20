<?php
// Get user input from either POST or GET method
$macAddress = $_REQUEST['mac_address'] ?? '';
$dhcpVersion = $_REQUEST['dhcp_version'] ?? '';

// Function to escape command line arguments
function escapeArgument($arg) {
    return escapeshellarg($arg);
}

// Call the Python script with user input
$command = sprintf(
    'python3 network_config.py %s %s',
    escapeArgument($macAddress),
    escapeArgument($dhcpVersion)
);
$html_output = shell_exec($command);
echo $html_output;
echo "<p><a href='form.php'>Back to input form</a></p>";
?>