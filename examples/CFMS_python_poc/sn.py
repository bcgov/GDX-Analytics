#See https://github.com/snowplow/snowplow/wiki/Python-Tracker
#   and https://github.com/snowplow-proservices/ca.bc.gov-schema-registry
from snowplow_tracker import Subject, Tracker, AsyncEmitter
from snowplow_tracker import SelfDescribingJson
import time
import random

# Set up core Snowplow environment
s = Subject()#.set_platform("app") 
e = AsyncEmitter("spm.gov.bc.ca", protocol="https")
t = Tracker(e, encode_base64=False, app_id = 'demo')

# get time stamp to create new "citizen" (be sure to convert to a string)
client_id = int(time.time())

# Set some sample values for example events
citizen = SelfDescribingJson( 'iglu:ca.bc.gov.cfmspoc/citizen/jsonschema/3-0-0',
     { "client_id": client_id, "service_count": 1, "quick_txn": False }
)

office = SelfDescribingJson( 'iglu:ca.bc.gov.cfmspoc/office/jsonschema/1-0-0',
     { "office_id": 8, "office_type": "non-reception" }
)

agent = SelfDescribingJson( 'iglu:ca.bc.gov.cfmspoc/agent/jsonschema/2-0-1',
    { "agent_id": 42, "role" : "CSR", "quick_txn": False }
)

# the addcitizen event has no parameters of its own so we pass an empty array "{}"
addcitizen = SelfDescribingJson( 'iglu:ca.bc.gov.cfmspoc/addcitizen/jsonschema/1-0-0', {})

# for chooseservices, we build a JSON array and pass it 
chooseservice = SelfDescribingJson('iglu:ca.bc.gov.cfmspoc/chooseservice/jsonschema/3-0-0',
    { "channel": "in-person", "program_id" : 100, "parent_id" : 0, "program_name":"example program name", "transaction_name":"example transaction name" }
)

beginservice = SelfDescribingJson( 'iglu:ca.bc.gov.cfmspoc/beginservice/jsonschema/1-0-0', {})

# --- Trigger a sequence of events with varying random wait times
# --- addcitizen ---
time.sleep(random.randint(0, 11)+3) 
t.track_self_describing_event (addcitizen, [citizen, office, agent]) 

# --- chooseservice ---
time.sleep(random.randint(0, 4)+2) 
t.track_self_describing_event (chooseservice, [citizen, office, agent])

# --- beginservice ---
time.sleep(random.randint(0, 6)+4) 
t.track_self_describing_event (beginservice, [citizen, office])
