#!/usr/bin/python
'''
# Python 2.7.9 script to download EventLogFiles
# Pre-requisite: standard library functionality = e.g urrlib2, json, StringIO

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
# Connected App information: fill it in by creating a connected app
# https://help.salesforce.com/articleView?id=connected_app_create.htm&language=en_US&type=0

CLIENT_ID = 'FILL_ME_IN'
CLIENT_SECRET = 'FILL_ME_IN'

#Imports

import urllib2
import json
#import ssl
import getpass
import os
import sys
import gzip
import time
from StringIO import StringIO
import base64

# login function
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

    print 'check point'
    # create a new salesforce REST API OAuth request
    url = 'https://login.salesforce.com/services/oauth2/token'
    data = '&grant_type=password&client_id='+CLIENT_ID+'&client_secret='+CLIENT_SECRET+'&username='+username+'&password='+password
    headers = {'X-PrettyPrint' : '1'}

    # workaround to ssl issue introduced before version 2.7.9
    #if hasattr(ssl, '_create_unverified_context'):
        #ssl._create_default_https_context = ssl._create_unverified_context

    # These lines are for when you have a proxy server
    # uncomment the next line to work with a local proxy server. replace the URL with the URL of your proxy
    # proxy = urllib2.ProxyHandler({'https': 'http://127.0.0.1:8888/'})
    # uncomment the next two lines if your proxy needs authentication. replace 'realm' through 'password' with appropriate values. 'realm' is often null
    # proxy_auth_handler = urllib2.HTTPBasicAuthHandler()
    # proxy_auth_handler.add_password('realm', 'host', 'username', 'password')
    # pick one of the next two lines based on whether you need proxy authentication. The first is authenticated, the second is unauthenticated
    # opener = urllib2.build_opener(proxy, proxy_auth_handler)
    # opener = urllib2.build_opener(proxy)
    # uncomment the final line to enable the proxy for any calls
    # urllib2.install_opener(opener)

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

# download function
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

    # check to see if anything
    if len(dir) < 1:
        dir = 'elf'
        print '\ndefault directory name used: ' + dir
    else:
        print '\ndirectory name used: ' + dir

    # If directory doesn't exist, create one
    if not os.path.exists(dir):
        os.makedirs(dir)

    # close connection
    res.close

    # check to see if the user wants to download it compressed
    compress = raw_input('\nUse compression (y/n)\n').lower()
    print compress

    # check to see if anything
    if len(compress) < 1:
        compress = 'yes'
        print '\ndefault compression being used: ' + compress
    else:
        print '\ncompression being used: ' + compress

    # loop over json elements in result and download each file locally
    for i in range(total_size):
        # pull attributes out of JSON for file naming
        ids = res_dict['records'][i]['Id']
        types = res_dict['records'][i]['EventType']
        dates = res_dict['records'][i]['LogDate']

        # create REST API request
        url = instance_url+'/services/data/v33.0/sobjects/EventLogFile/'+ids+'/LogFile'

        # provide correct compression header
        if (compress == 'y') or (compress == 'yes'):
            headers = {'Authorization' : 'Bearer ' + access_token, 'X-PrettyPrint' : '1', 'Accept-encoding' : 'gzip'}
            print 'Using gzip compression\n'
        else:
            headers = {'Authorization' : 'Bearer ' + access_token, 'X-PrettyPrint' : '1'}
            print 'Not using gzip compression\n'

        # begin profiling
        start = time.time()

        # open connection
        req = urllib2.Request(url, None, headers)
        res = urllib2.urlopen(req)

        print '********************************'

        # provide feedback to user
        print 'Downloading: ' + dates[:10] + '-' + types + '.csv to ' + os.getcwd() + '/' + dir + '\n'

        # print the response to see the content type
        # print res.info()

        # if the response is gzip-encoded as expected
        # compression code from http://bit.ly/pyCompression
        if res.info().get('Content-Encoding') == 'gzip':
            # buffer results
            buf = StringIO(res.read())
            # gzip decode the response
            f = gzip.GzipFile(fileobj=buf)
            # print data
            data = f.read()
            # close buffer
            buf.close()
        else:
            # buffer results
            buf = StringIO(res.read())
            # get the value from the buffer
            data = buf.getvalue()
            #print data
            buf.close()

        # write buffer to CSV with following naming convention yyyy-mm-dd-eventtype.csv
        file = open(dir + '/' +dates[:10]+'-'+types+'.csv', 'w')
        file.write(data)

        # end profiling
        end = time.time()
        secs = end - start

        #msecs = secs * 1000  # millisecs
        #print 'elapsed time: %f ms' % msecs
        print 'Total download time: %f seconds\n' % secs

        file.close
        i = i + 1

        # close connection
        res.close

download_elf()
