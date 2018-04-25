/******************************************************************************
 * Proof of concept code for CFMS Instrumentation project
 * NOTE: There is a bug right now that doesn't close the session correctly
 *   As a result the program may seem to hang when running
 *   If it logs "SimpleEmitter successfully sent 1 events: code: 200", then 
 *      it was successful, even if it doesn't close out
 ******************************************************************************/

package ca.bc.gov.CFMS_poc;

import com.snowplowanalytics.snowplow.tracker.DevicePlatform;
import com.snowplowanalytics.snowplow.tracker.Tracker;
import com.snowplowanalytics.snowplow.tracker.emitter.SimpleEmitter;
import com.snowplowanalytics.snowplow.tracker.emitter.BatchEmitter;
import com.snowplowanalytics.snowplow.tracker.emitter.Emitter;
import com.snowplowanalytics.snowplow.tracker.emitter.RequestCallback;
import com.snowplowanalytics.snowplow.tracker.events.PageView;
import com.snowplowanalytics.snowplow.tracker.events.Unstructured;
import com.snowplowanalytics.snowplow.tracker.payload.SelfDescribingJson;
import com.snowplowanalytics.snowplow.tracker.http.HttpClientAdapter;
import com.snowplowanalytics.snowplow.tracker.http.OkHttpClientAdapter;
import com.snowplowanalytics.snowplow.tracker.payload.TrackerPayload;
import com.squareup.okhttp.OkHttpClient;

import java.util.List;
import java.util.concurrent.TimeUnit;


import java.util.HashMap;
import java.util.ArrayList;
import java.util.Map;

public class App {
    //========================================
    // For now we are harcoding the tracker URL here. There are two options
    //     Snowplow Mini: spm.gov.bc.ca -- for early tracking. Real-time view for GDX, but not pushed into real repo. (This is not connected to Looker.)
    //     Snowplow Real Tracker: https://ca-bc-gov-main.collector.snplow.net -- the "real" tracker. This URL will change for the live service. Data pushed here is pushed into the real Snowplow, connected to Looker. 
    //private static final String collectorEndpoint = "https://ca-bc-gov-main.collector.snplow.net";
    private static final String collectorEndpoint = "https://spm.gov.bc.ca";
 

    //========================================
    // Set up the namespace and appID
    private static final String namespace = "CFMS_poc";
    private static final String appID = "demo";
    //========================================
    // Set whether or not to send events base64 encoded. For now, we send nonencoded to ease debugging
    private static final Boolean baseSetting = false; 

    //========================================
    public static HttpClientAdapter getClient(String url) {
        // use okhttp to send events
        OkHttpClient client = new OkHttpClient();

        client.setConnectTimeout(5, TimeUnit.SECONDS);
        client.setReadTimeout(5, TimeUnit.SECONDS);
        client.setWriteTimeout(5, TimeUnit.SECONDS);

        return OkHttpClientAdapter.builder()
                .url(url)
                .httpClient(client)
                .build();
    }

    public static void main(String[] args) {
        // get the client adapter
        // this is used by the Java tracker to transmit events to the collector
        HttpClientAdapter okHttpClientAdapter = getClient(collectorEndpoint);
    
        Emitter emitter = SimpleEmitter.builder()
                .httpClientAdapter( okHttpClientAdapter ) // Required
                .threadCount(20) // Default is 50
                .build();
                
        
        Tracker tracker = new Tracker.TrackerBuilder(emitter, namespace, appID)
                            .base64(baseSetting)
                            .platform(DevicePlatform.Desktop)
                            .build();
    
    //----------------------------------------
    // Create a Map of the data you want to include...
    Map<String, Object> citizenMap = new HashMap<>();
    citizenMap.put("client_id", 111111);
    citizenMap.put("quick_txn", false);
    SelfDescribingJson citizen = new SelfDescribingJson("iglu:ca.bc.gov.cfmspoc/citizen/jsonschema/1-1-0", citizenMap);

    //----------------------------------------
    Map<String, Object> officeMap = new HashMap<>();
    officeMap.put("office_id", 12);
    officeMap.put("office_type", "reception");
    SelfDescribingJson office = new SelfDescribingJson("iglu:ca.bc.gov.cfmspoc/office/jsonschema/1-0-0", officeMap);
    
    //----------------------------------------
    Map<String, Object> agentMap = new HashMap<>();
    agentMap.put("agent_id", 12);
    agentMap.put("role", "CSR");
    agentMap.put("quick_txn", true);
    SelfDescribingJson agent = new SelfDescribingJson("iglu:ca.bc.gov.cfmspoc/agent/jsonschema/1-1-0", agentMap);
    
    //----------------------------------------
    List<SelfDescribingJson> contexts = new ArrayList<>();
    contexts.add(citizen);
    contexts.add(office);
    contexts.add(agent);
    
    // Create your event data -- in this example the event has data of its own
    Map<String, Object> chooseserviceMap = new HashMap<>();
    chooseserviceMap.put("channel","in-person");
    chooseserviceMap.put("program_id",12);
    chooseserviceMap.put("parent_id",0);
    chooseserviceMap.put("program_name","An amazing program");
    chooseserviceMap.put("transaction_name","A fantastic transaction");
    chooseserviceMap.put("quick_txn",false);

    SelfDescribingJson chooseserviceData = new SelfDescribingJson("iglu:ca.bc.gov.cfmspoc/chooseservice/jsonschema/1-0-0", chooseserviceMap);
    // Track your event with your custom event data
    tracker.track(Unstructured.builder()
        .eventData(chooseserviceData)
        .customContext(contexts)
        .build());

    //----------------------------------------
    // Create your event data -- in this example the event has no data of its own
    SelfDescribingJson beginserviceData = new SelfDescribingJson("iglu:ca.bc.gov.cfmspoc/beginservice/jsonschema/1-0-0");
    // Track your event with your custom event data
    tracker.track(Unstructured.builder()
        .eventData(beginserviceData)
        .customContext(contexts)
        .build());
    }
} 
