<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Input Form</title>
</head>
<body>
    <h2>Python Network Configuration Tool</h2>
    <form action="process.php" method="POST">
        <div>
            <label for="mac_address">Mac Address:</label>
            <input type="text" id="mac_address" name="mac_address" required/>
        </div>
        <div>
            <label for="dhcp_version">DHCP Version:</label>
            <select id="dhcp_version" name="dhcp_version" required>
                <option value="DHCPv4">DHCPv4</option>
                <option value="DHCPv6">DHCPv6</option>
            </select>
        </div>
        <button type="submit">Submit</button>
    </form>
</body>
</html>