# Connected App information: fill it in by creating a connected app
# https://help.salesforce.com/articleView?id=connected_app_create.htm&language=en_US&type=0


#Imports
import urllib.request
import json
import getpass
import os
import sys
import gzip
import time
from io import StringIO
import base64

# login function
def login():
    ''' Login to salesforce service using OAuth2 '''
    # username = ''
    # password = ''
    # clientId = ''
    # clientSecret = ''
    # prompt for username, password, consumer key and consumer secret
    # while len(username) < 1:
    print('Remember, you need data from a Connected App')
    username = input('Username: ')
    # while len(password) < 1:
    password = getpass.getpass('Password:')
    # while len(clientId) < 1:
    clientId = input('Consumer key: ')
    # while len(clientSecret) < 1:
    clientSecret = input('Consumer secret: ')
    instanceType = input('Instance type (login by default): ')

    # check to see if anything was entered and if not, default values
    # change default values for username and password to your own
    if len(username) < 1:
        username = 'you@mail.com'
        password = 'PasswordToken'
        clientId = 'Yourclientid'
        clientSecret = 'Yourclientsecret'
        print('Using default username and credentials: {0}'.format(username))
    else:
        print('Using user inputed username and credentials: {0}'.format(username))
    # Use 'login' by default
    if len(instanceType) < 1:
        instanceType = 'login'

    print('check point')
    # create a new salesforce REST API OAuth request
    url = 'https://' + instanceType + '.salesforce.com/services/oauth2/token'
    dataUnencoded = {
        'grant_type': 'password',
        'client_id': clientId,
        'client_secret': clientSecret,
        'redirect_uri': 'YourRedirectURI',
        'username': username,
        'password': password
        }
    data = urllib.parse.urlencode(dataUnencoded).encode("utf-8")
    headers = {'X-PrettyPrint' : '1'}
    # call salesforce REST API and pass in OAuth credentials
    req = urllib.request.Request(url, data, headers = headers)
    try:
        res = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        if(e.reason == 'Bad Request'):
            print('Error: {0}, check input data'.format(e.reason))
        else:
            print('Error: {0}'.format(e.reason))
        sys.exit()

    # return OAuth access token necessary for additional REST API calls
    access_token = res_dict['access_token']
    instance_url = res_dict['instance_url']

    return access_token, instance_url

# download function
def download_elf():
    ''' Query salesforce service using REST API '''
    # login and retrieve access_token and day
    access_token, instance_url = login()

    day = input('\nDate range (e.g. Last_n_Days:2, Today, Tomorrow):\n')

    # check to see if anything was entered and if not, default values
    if len(day) < 1:
        day = 'Last_n_Days:2'
        print('Using default date range: {0} \n'.format(day))
    else:
        print('Using user inputed date range: {0} \n'.format(day))

    # query Ids from Event Log File
    url = instance_url+'/services/data/v41.0/query?q=SELECT+Id+,+EventType+,+Logdate+From+EventLogFile+Where+LogDate+=+'+day
    headers = {'Authorization' : 'Bearer ' + access_token, 'X-PrettyPrint' : '1'}
    req = urllib.request.Request(url, None, headers = headers)
    res = urllib.request.urlopen(req)
    res_dict = json.load(res)

    # capture record result size to loop over
    total_size = res_dict['totalSize']

    # provide feedback if no records are returned
    if total_size < 1:
        print('No records were returned for {0}'.format(day))
        sys.exit()

    # create a directory for the output
    dir = input("Output directory: ")

    # check to see if anything
    if len(dir) < 1:
        dir = 'elf'
        print('\ndefault directory name used: {0}'.format(dir))
    else:
        print('\ndirectory name used: {0}'.format(dir))

    # If directory doesn't exist, create one
    if not os.path.exists(dir):
        os.makedirs(dir)

    # close connection
    res.close

    # check to see if the user wants to download it compressed
    # compress = input('\nUse compression (y/n)\n').lower()
    # print(compress)
    # Disabled compress validation meanwhile...
    compress = 'n'

    # check to see if anything
    if len(compress) < 1:
        compress = 'yes'
        print('\ndefault compression being used: {0}'.format(compress))
    else:
        print('\ncompression being used: {0}'.format(compress))

    # loop over json elements in result and download each file locally
    for i in range(total_size):
        # pull attributes out of JSON for file naming
        ids = res_dict['records'][i]['Id']
        types = res_dict['records'][i]['EventType']
        dates = res_dict['records'][i]['LogDate']

        # create REST API request
        url = instance_url+'/services/data/v41.0/sobjects/EventLogFile/'+ids+'/LogFile'

        # provide correct compression header
        if (compress == 'y') or (compress == 'yes'):
            headers = {'Authorization' : 'Bearer ' + access_token, 'X-PrettyPrint' : '1', 'Accept-encoding' : 'gzip'}
            print('Using gzip compression\n')
        else:
            headers = {'Authorization' : 'Bearer ' + access_token, 'X-PrettyPrint' : '1'}
            print('Not using gzip compression\n')

        # begin profiling
        start = time.time()

        # open connection
        req = urllib.request.Request(url, None, headers)
        res = urllib.request.urlopen(req)

        print('********************************')

        # provide feedback to user
        print('Downloading: ' + dates[:10] + '-' + types + '.csv to ' + os.getcwd() + '/' + dir + '\n')

        # print the response to see the content type
        # print res.info()

        # if the response is gzip-encoded as expected
        # compression code from http://bit.ly/pyCompression
        if res.info().get('Content-Encoding') == 'gzip':
            # buffer results
            html = res.read()
            decodedHtml = html.decode('iso-8859-1')#.encode('UTF-8')
            # decodedHtml = decodedHtml.decode('UTF-8')
            print('HTML=>', decodedHtml)
            buf = StringIO(decodedHtml)
            # gzip decode the response
            f = gzip.GzipFile(fileobj=buf)
            # print data
            data = f.read()
            # close buffer
            buf.close()
        else:
            # buffer results
            buf = StringIO(res.read().decode('utf-8'))
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
        print('Total download time: %f seconds\n' % secs)

        file.close
        i = i + 1

        # close connection
        res.close

download_elf()