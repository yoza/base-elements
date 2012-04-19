import urllib2
import json
import base64

def get_resource(request, authuser=None, authpass=None):
    msg_error = []
    try:
        opener = urllib2.urlopen(request)
    except urllib2.URLError, e:
        msg_error = e
        if e.code and e.code == 401 and 'unauthorized' in e.msg.lower():
            try:
                #Next two string for htpass
                msg_error = []
                if authuser:
                    base64string = base64.encodestring('%s:%s' % (authuser, authpass)).replace('\n', '')
                    request.add_header("Authorization", "Basic %s" % base64string)
                opener = urllib2.urlopen(request)
            except urllib2.URLError, e:
                msg_error = e
    if not msg_error:
        return json.load(opener)
    return None