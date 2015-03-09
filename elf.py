# !/usr/bin/python
'''
# Python 2.7.9 script to download EventLogFiles
# Pre-requisite: standard library functionality = urrlib2, json, StringIO

 #/**
 #* Copyright (c) 2012, Salesforce.com, Inc.  All rights reserved.
 #*
 #* Redistribution and use in source and binary forms, with or without
 #* modification, are permitted provided that the following conditions are
 #* met:
 #*
 #*   * Redistributions of source code must retain the above copyright
 #*     notice, this list of conditions and the following disclaimer.
 #*
 #*   * Redistributions in binary form must reproduce the above copyright
 #*     notice, this list of conditions and the following disclaimer in
 #*     the documentation and/or other materials provided with the
 #*     distribution.
 #*
 #*   * Neither the name of Salesforce.com nor the names of its
 #*     contributors may be used to endorse or promote products derived
 #*     from this software without specific prior written permission.
 #*
 #* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 #* "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 #* LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 #* A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 #* HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 #* SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 #* LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 #* DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 #* THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 #* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 #* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 #*/
'''
# Configurations - change to fit your org

CLIENT_ID = '3MVG99OxTyEMCQ3ilfR5dFvVjgTrCbM3xX8HCLLS4GN72CCY6q86tRzvtjzY.0.p5UIoXHN1R4Go3SjVPs0mx'
CLIENT_SECRET = '7899378653052916471'

#Code

import urllib2
import json
from StringIO import StringIO
import ssl
import getpass
import os
import sys

def login():
    ''' Login to salesforce service using OAuth2 '''
    # prompt for username and password
    username = raw_input('Username: \n')
    password = getpass.getpass('Password: \n')

    # check to see if anything was entered and if not, default values
    # change default values for username and password to your own
    if len(username) < 1:
        username = 'user@company.com'
        password = 'Passw0rd'
        print 'Using default username: ' + username
    else:
        print 'Using user inputed username: ' + username

    # create a new salesforce REST API OAuth request
    url = 'https://login.salesforce.com/services/oauth2/token'
    data = '&grant_type=password&client_id='+CLIENT_ID+'&client_secret='+CLIENT_SECRET+'&username='+username+'&password='+password
    headers = {'X-PrettyPrint' : '1'}
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    # call salesforce REST API and pass in OAuth credentials
    req = urllib2.Request(url, data, headers)
    res = urllib2.urlopen(req)

    # load results to dictionary
    res_dict = json.load(res)

    # close connection
    res.close()

    # return OAuth access token necessary for additional REST API calls
    access_token = res_dict['access_token']
    instance_url = res_dict['instance_url']

    return access_token, instance_url

def download_elf():
    ''' Query salesforce service using REST API '''
    # login and retrieve access_token and day
    access_token, instance_url = login()

    day = raw_input('\nDate range (e.g. Last_n_Days:2, Today, Tomorrow):\n')

    # check to see if anything was entered and if not, default values
    if len(day) < 1:
        day = 'Last_n_Days:2'
        print 'Using default date range: ' + day + '\n'
    else:
        print 'Using user inputed date range: ' + day + '\n'

    # query Ids from Event Log File
    url = instance_url+'/services/data/v33.0/query?q=SELECT+Id+,+EventType+,+Logdate+From+EventLogFile+Where+LogDate+=+'+day
    headers = {'Authorization' : 'Bearer ' + access_token, 'X-PrettyPrint' : '1'}
    req = urllib2.Request(url, None, headers)
    res = urllib2.urlopen(req)
    res_dict = json.load(res)

    # capture record result size to loop over
    total_size = res_dict['totalSize']

    # provide feedback if no records are returned
    if total_size < 1:
        print 'No records were returned for ' + day
        sys.exit()

    # create a directory for the output
    dir = raw_input("Output directory: ")

    # check to see if anything was entered and if not, default values
    if len(dir) < 1:
        dir = 'elf_downloads'

    # If directory doesn't exist, create one
    if not os.path.exists(dir):
        os.makedirs(dir)

    # close connection
    res.close

    # loop over json elements in result and download each file locally
    for i in range(total_size):
        # pull attributes out of JSON for file naming
        ids = res_dict['records'][i]['Id']
        types = res_dict['records'][i]['EventType']
        dates = res_dict['records'][i]['LogDate']

        # create REST API request
        url = instance_url+'/services/data/v33.0/sobjects/EventLogFile/'+ids+'/LogFile'
        headers = {'Authorization' : 'Bearer ' + access_token, 'X-PrettyPrint' : '1'}
        req = urllib2.Request(url, None, headers)
        res = urllib2.urlopen(req)

        # provide feedback to user
        print 'Downloading: ' + dates[:10] + '-' + types + '.csv to ' + os.getcwd() + '/' + dir

        # buffer results and close connection
        buffer = StringIO(res.read())
        data = buffer.getvalue()
        res.close()

        # write buffer to CSV with following naming convention yyyy-mm-dd-eventtype.csv
        file = open(dir + '/' +dates[:10]+'-'+types+'.csv', 'w')
        file.write(data)
        file.close
        i = i + 1

download_elf()
