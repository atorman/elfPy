## A Simple Python Script for Downloading EventLogFiles

### Pre-requisites

Elf.py is built on the Python Standard Library. Your script will automatically import the following modules:

* import urllib2
* import json
* from StringIO import StringIO
* import ssl
* import getpass
* import os
* import sys

As a result, there shouldn't be a need to install any other modules. However, you should verify that you have version 2.7.9 of python. Open a terminal (or cmd in Windows) and type:

      $ python --version

You should see

      Python 2.7.9

If you do not, you may need to install it: https://www.python.org/downloads/release/python-279/

If you have multiple versions of python installed, you can declare which version you want on the command line:

      $ python2.7 --version

For more information, read the help topic (https://docs.python.org/3/installing/#work-with-multiple-versions-of-python-installed-in-parallel).

### Download

To use this script, just click the Download ZIP button in GitHub and store locally on your laptop or desktop.

### Run Script

From the terminal, navigate to the directory where you downloaded elf.py. For instance

      $ cd ~/Users/atorman/Desktop

To run the script, type:

      $ python elf.py

You will be prompted for several inputs:
1. Username
2. Password (hidden)
3. Date range (recommend: *Last_n_Days:2* instead of Yesterday)
4. Output directory

It's possible to change the defaults for these four prompts within the code. I recommend this if you want to test or automate the script.

The output will be an Event Log File CSV (Comma Separated Values) file for each day in the date range with the following file name convention: yyyy-mm-dd-eventtype.csv. For instance:

      2015-03-08-Login.csv

### Troubleshooting

I tested this script on Ubuntu Linux, Mac OSX, and Microsoft Windows platform. However, that doesn't mean you won't run into problems.

One issue I did encounter was the use of a security token with your password if you are in a non-whitelisted organization or profile. Many administrators won't encounter this but if you try to log into the API without the token, you'll be blocked.

To reset your token, go to My Settings | Personal | Reset My Security Token. 

If you don't see this menu item, then a security token is *not* required.

When entering your password with a security token, the token follows your password:

If your password = "mypassword"
And your security token = "XXXXXXXXXX"
You must enter "mypasswordXXXXXXXXXX" in place of your password

You can also read more about this in the help topic (https://help.salesforce.com/htviewhelpdoc?id=user_security_token.htm&siteLang=en_US).

You may also encounter a login error due to the ClientId and ClientSecret. If you do, make sure to change the constants in elf.py to reflect your own ClientId and ClientSecret. You can read more about how to create your own ClientId and ClientSecret in the help topic (https://help.salesforce.com/HTViewHelpDoc?id=connected_app_create.htm&language=en_US).

### Supported platforms

Supported platforms: MacOS, Linux, and Windows.  

## Getting help

tweet to @atorman:

* http://twitter.com/atorman

or post a comment to Salesforcehacker.com

* http://www.salesforcehacker.com
