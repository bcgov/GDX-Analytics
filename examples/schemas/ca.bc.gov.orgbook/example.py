#  See https://github.com/snowplow/snowplow/wiki/Python-Tracker
#     and https://github.com/snowplow-proservices/ca.bc.gov-schema-registry

import time
import random
from snowplow_tracker import Subject, Tracker, AsyncEmitter
from snowplow_tracker import SelfDescribingJson


# Set up core Snowplow environment
s = Subject()
e = AsyncEmitter("spm.apps.gov.bc.ca", protocol="https")
t = Tracker(e, encode_base64=False, app_id='orgbook_api')


search_json = SelfDescribingJson( 'iglu:ca.bc.gov.orgbook/api_call/jsonschema/1-0-0', {
  'internal_call': False,
  'api_version': 'v3',
  'endpoint': 'search/topic',
  'total': 1,
  'response_time': 67,
  'parameters': ['name']
})

credentials_json = SelfDescribingJson( 'iglu:ca.bc.gov.orgbook/api_call/jsonschema/1-0-0', {
  'internal_call': False,
  'api_version': 'v3',
  'endpoint': 'credentials',
  'total': 2,
  'response_time': 102,
  'parameters': ['topic_id']
})

t.track_self_describing_event(search_json)
time.sleep(5)
t.track_self_describing_event(credentials_json)
time.sleep(5)
