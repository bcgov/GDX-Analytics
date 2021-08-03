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

# Example Snowplow for an external API V3 call to "/search/topic?name=BC0772006"
search_json = SelfDescribingJson( 'iglu:ca.bc.gov.orgbook/api_call/jsonschema/1-0-0', {
  'internal_call': False,
  'api_version': 'v3',
  'endpoint': 'search/topic',
  'total': 1,
  'response_time': 67,
  'parameters': ['name']
})

# Example Snowplow for an external API V3 call to "/credentialtype"
credentialtype_json = SelfDescribingJson( 'iglu:ca.bc.gov.orgbook/api_call/jsonschema/1-0-0', {
  'internal_call': False,
  'api_version': 'v3',
  'endpoint': 'credentialtype',
  'response_time': 102,
  'total': 6
})

# Example Snowplow for an external API V3 call to "/credentialtype/1/language"
credentialtype_language_json = SelfDescribingJson( 'iglu:ca.bc.gov.orgbook/api_call/jsonschema/1-0-0', {
  'internal_call': False,
  'api_version': 'v3',
  'endpoint': 'credentialtype/{id}/language',
  'response_time': 302,
  'total': 1,
  'parameters': ['id']
})

t.track_self_describing_event(search_json)
time.sleep(5)
t.track_self_describing_event(credentialtype_json)
time.sleep(5)
t.track_self_describing_event(credentialtype_language_json)
time.sleep(5)
