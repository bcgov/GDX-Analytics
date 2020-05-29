###################################################################
# Script Name   : looker_embed_generator.py
#
# Description   : Sample Python script to generate secure Looker
#               : embed codes that include custom filters.
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the embed user
#
#               : export LOOKERKEY=<<Looker embed key>>
#
# Usage         : To create an embed string without a filter:
#               : python looker_embed_generator.py <<embed url>>
#               :
#               : eg: python looker_embed_generator.py dashboards/18
#               :
#               : To create an embed string with filter(s):
#               :
#               : 1 Filter and 1 Value
#               :
#               : python looker_embed_generator.py <<embed url>>
#               :   '{"filter-name": {"matchtype": "matchtype-value", 
#               :                     "values":"filter-value"}'
#               :
#               : eg: python looker_embed_generator.py dashboards/18
#               :   '{"City":["matchtype":"=", "values":"Metropolis"]}'
#               :
#               : or:
#               : 
#               : 1 Filter and 2 or more Values
#               :
#               : python looker_embed_generator.py <<embed url>>
#               :   '{"filter-name": ["matchtype": {"matchtype-value","values":"filter-value"},
#               :                                  {"matchtype-value","values":"filter-value"}]}'
#               :
#               : eg: python looker_embed_generator.py dashboards/18
#               :   '{"City":[{"matchtype":"=", "values":"Duncan - British Columbia"},
#               :             {"matchtype":"starts", "values":"Nanaimo - British Columbia"}]}'
#               :
#               : or:
#               : 
#               : 2 Filter and 1 Value
#               :
#               : python looker_embed_generator.py <<embed url>>
#               :   '{"filter-name": ["matchtype": {"matchtype-value","values":"filter-value"}],
#               :    "filter-name": ["matchtype": {"matchtype-value","values":"filter-value"}]}'
#               :
#               : eg: python looker_embed_generator.py dashboards/snowplow_web_block::bc_gov_analytics_dashboard_1 
#               :   '{"City":[{"matchtype":"=","values":"Victoria - British Columbia"}, 
#               :     "City":[{"matchtype":"contains","values":"Vancouver - British Columbia"}]}'
#               :
#               : or:
#               : 
#               : 1 Filter and comma separated values
#               :
#               : python looker_embed_generator.py <<embed url>>
#               :   '{"filter-name": ["matchtype": "matchtype-value", 
#               :                     "values":"filter-value"]}'
#               :
#               : :python looker_embed_generator.py dashboards/18
#               :   '{"Theme": ["matchtype": "=", 
#               :               "values":"\"Birth, Adoption, Death, Marriage & Divorce\",\"Employment, Business & Economic Development\""]}'
#               :
#               :
#               : List of valid match types:
#               :
#               : Is equal to: '='
#               : Contains: 'contains'
#               : Does not contain: '!contains'
#               : Starts with: 'starts'
#               : Is empty: 'empty'
#               : Is null: 'null'
#               : Is not equal to: '!='
#               : Does not contain: '!contains'
#               : Does not start with: '!starts'
#               : Does not end with: '!ends'
#               : Is not empty: '!empty'
#               : Is not null: '!null'
#               : Matches a user attribute: 'user_attribute'
#               :
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


# Add double slashes before commas and then URI encode.
# The double slashes are required due to how looker parses
# filter parameters in the embed_url string.
def parse_filter_value(filter_value):
    parsed_filter_value = urllib.quote(filter_value.replace(', ', r'\\, ').replace('\"',''))
    return parsed_filter_value


# This function loops over the filters passed into the script and
# generates the filters section of the embed url string.
def encode_embed_filters(filters):
    embed_url_string = "?filter_config=%7B"
    filter_string = ''
    index = 1
    for filter_name in filters:
        filter_string += "\"" + filter_name + "\":%5B"
        filter_string += build_filter_string(filters[filter_name])
        if index < len(filters):
            filter_string += ","
        index += 1
    return embed_url_string + filter_string + "%7D"


# This function loops over each filter value and generates the
# the strings for individual filter values
def build_filter_string(filter_values):
    filter_string = ""
    index = 1
    for filter_value in filter_values:
        match_type = filter_value["matchtype"]
        value = parse_filter_value(filter_value["values"])
        filter_string += "%7B\"type\":\"" + match_type + \
            "\",\"values\":%5B%7B\"constant\":\"" + \
            value + "\"%7D,%7B%7D%5D%7D"
        if index < len(filter_values):
            filter_string += ","
        elif index == len(filter_values):
            filter_string += "%5D"
        index += 1
    return filter_string


# Set up flag for filters
filtered = False

# Set configuration
if (len(sys.argv) < 2):  # Will be 1 if no arguments, 2 if one argument
    print "Usage: python looker_embed_generator.py \
        <<embed url>> {\"filtername\": \"filtervalue\"}"
    sys.exit(1)

if (len(sys.argv) == 3):  # Will be 3 if passing in a json object of filters
    filtered = True
    filters = json.loads(sys.argv[2])

embed_url = '/embed/' + sys.argv[1]

# If the filtered flag is set, break out the filter names and values
# from the JSON string passed in via cms line, and add these to the
# embed_url string.
if filtered:
    embed_url += encode_embed_filters(filters)

lookerkey = os.getenv('LOOKERKEY')

if (lookerkey is None):  # confirm that the environment variable is set
    print "LOOKERKEY environment variable not set"
    sys.exit(1)

lookerurl = 'dev.analytics.gov.bc.ca'  # set to the URL where Looker is hosted


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

    url = URL(looker, user, timeout, embed_url + ('&' if filtered else '?') +
              'embed_domain=http://localhost:8888', force_logout_login=True)

    return "https://" + url.to_string()


print test()
