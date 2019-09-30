###################################################################
# Script Name   : looker_embed_generator.py
#
# Description   : Sample Python script to generate secure Looker
#               : embed codes that include custom filters.
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the embed user
#
#               : export export LOOKERKEY=<<Looker embed key>>
#
# Usage         : To create an embed string without a filter:
#               : python looker_embed_generator.py <<embed url>>
#               :
#               : eg: python looker_embed_generator.py dashboards/18
#               :
#               : To create an embed string with a filter:
#               :
#               : python looker_embed_generator.py <<embed url>>
#               :   [<<filter name>> <<filter value>>]
#               :
#               : eg: python looker_embed_generator.py dashboards/18
#               :   Theme "Birth, Death, Adoption, Marriage and Divorce"
#               :
#               : NOTE: The embed must be accessible to the
#               : Embed Shared Group.
#               :
# References    : https://docs.looker.com/reference/embedding/
#               :   sso-embed#building_the_embed_url
#               : https://docs.looker.com/reference/embedding/
#               :   embed-javascript-events
#               :

import urllib
import base64
import json
import time
import binascii
import os
from hashlib import sha1
import hmac
import sys  # to read command line parameters


def parse_filter_value(filter_value):
    parsed_filter_value = urllib.quote(filter_value.replace(',', r'\\,'))
    return parsed_filter_value


# Set up variables for filters
filter_value = ''
filter_name = ''
filtered = False

# Set configuration
if (len(sys.argv) < 2):  # Will be 1 if no arguments, 2 if one argument
    print "Usage: python looker_embed_generator.py \
        <<embed url>> [<<filter-name>> <<filter-value>>]"
    sys.exit(1)

if (len(sys.argv) == 3):
    print "Usage: python looker_embed_generator.py \
        <<embed url>> [<<filter-name>> <<filter-value>>]"
    sys.exit(1)

if (len(sys.argv) == 4):
    filtered = True
    filter_name = sys.argv[2]
    filter_value = parse_filter_value(sys.argv[3])

embedurl = '/embed/' + sys.argv[1]

if filtered:
    embedurl += "?filter_config=%7B\"" + filter_name + \
      "\":%5B%7B\"type\":\"%3D\",\"values\":%5B%7B\"constant\":\"" + \
      filter_value + "\"%7D,%7B%7D%5D,\"id\":456%7D%5D%7D"

lookerkey = os.getenv('LOOKERKEY')
if (lookerkey is None):  # confirm that the environment variable is set
    print "LOOKERKEY environment variable not set"
    sys.exit(1)

lookerurl = '52.60.65.121:9999'  # set to the URL where Looker is hosted

class Looker:
    def __init__(self, host, secret):
        self.secret = secret
        self.host = host


class User:
    def __init__(self, id=id, first_name=None, last_name=None,
                 permissions=[], models=[], group_ids=[],
                 external_group_id=None,
                 user_attributes={}, access_filters={}):
        self.external_user_id = json.dumps(id)
        self.first_name = json.dumps(first_name)
        self.last_name = json.dumps(last_name)
        self.permissions = json.dumps(permissions)
        self.models = json.dumps(models)
        self.access_filters = json.dumps(access_filters)
        self.user_attributes = json.dumps(user_attributes)
        self.group_ids = json.dumps(group_ids)
        self.external_group_id = json.dumps(external_group_id)


class URL:
    def __init__(self, looker, user, session_length,
                 embed_url, force_logout_login=False):
        self.looker = looker
        self.user = user
        self.path = '/login/embed/' + urllib.quote_plus(embed_url)
        self.session_length = json.dumps(session_length)
        self.force_logout_login = json.dumps(force_logout_login)

    # The current time as a UNIX timestamp.
    def set_time(self):
        self.time = json.dumps(int(time.time()))

    # Random string cannot be repeated within an hour. Prevents an
    # attacker from re-submitting a legitimate user's URL to gather
    # information they shouldn't have.
    def set_nonce(self):
        self.nonce = json.dumps(binascii.hexlify(os.urandom(16)))

    def sign(self):
        #  Do not change the order of these
        string_to_sign = ""
        string_to_sign = string_to_sign + self.looker.host + "\n"
        string_to_sign = string_to_sign + self.path + "\n"
        string_to_sign = string_to_sign + self.nonce + "\n"
        string_to_sign = string_to_sign + self.time + "\n"
        string_to_sign = string_to_sign + self.session_length + "\n"
        string_to_sign = string_to_sign + self.user.external_user_id + "\n"
        string_to_sign = string_to_sign + self.user.permissions + "\n"
        string_to_sign = string_to_sign + self.user.models + "\n"
        string_to_sign = string_to_sign + self.user.group_ids + "\n"
        string_to_sign = string_to_sign + self.user.external_group_id + "\n"
        string_to_sign = string_to_sign + self.user.user_attributes + "\n"
        string_to_sign = string_to_sign + self.user.access_filters

        signer = hmac.new(self.looker.secret,
                          string_to_sign.encode('utf8'), sha1)
        self.signature = base64.b64encode(signer.digest())

    def to_string(self):
        self.set_time()
        self.set_nonce()
        self.sign()

        params = {'nonce':               self.nonce,
                  'time':                self.time,
                  'session_length':      self.session_length,
                  'external_user_id':    self.user.external_user_id,
                  'permissions':         self.user.permissions,
                  'group_ids':           self.user.group_ids,
                  'models':              self.user.models,
                  'external_group_id':   self.user.external_group_id,
                  'user_attributes':     self.user.user_attributes,
                  'access_filters':      self.user.access_filters,
                  'signature':           self.signature,
                  'first_name':          self.user.first_name,
                  'last_name':           self.user.last_name,
                  'force_logout_login':  self.force_logout_login}

        query_string = '&'.join(["%s=%s" % (key,
                                            urllib.quote_plus(val)) for key,
                                val in params.iteritems()])

        return "%s%s?%s" % (self.looker.host, self.path, query_string)


def test():
    looker = Looker(lookerurl, lookerkey)

    user = User(50,
                first_name='Dashboard',
                last_name='User',
                permissions=['see_lookml_dashboards', 'access_data',
                             'see_user_dashboards', 'see_looks'],
                models=['all'],
                # group_ids=[1,54],
                external_group_id='external_group_id',
                # Add additional filters here. They must match a user
                # attribute that is listed in the LookML with an access_filter}
                user_attributes={"can_see_sensitive_data": "YES"}
                )

    # Set TTL for embed code. 60*15 = 15 minutes
    timeout = 60 * 15

    url = URL(looker, user, timeout, embedurl + ('&' if filtered else '?') +
              'embed_domain=http://127.0.0.1:5000', force_logout_login=True)

    return "https://" + url.to_string()


print test()