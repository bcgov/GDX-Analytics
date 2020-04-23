// <!-- Snowplow starts plowing - Search vA.2.10.2 -->
;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
    p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
    };p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
    n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","https://sp-js.apps.gov.bc.ca/MDWay3UqFnIiGVLIo7aoMi4xMC4y.js","snowplow"));
    var collector = 'spm.apps.gov.bc.ca';
    window.snowplow('newTracker','rt',collector, {
        appId: "Snowplow_gov",
        platform: 'web',
        post: true,
        forceSecureTracker: true,
        contexts: {
            webPage: true,
            performanceTiming: true
        }
    });
    window.snowplow('enableActivityTracking', 30, 30); // Ping every 30 seconds after 30 seconds
    window.snowplow('enableLinkClickTracking');
    window.snowplow('trackPageView',null,
      [{
        schema: 'iglu:ca.bc.gov/meta_data/jsonschema/1-0-0',
        data: {
          node_id: document.querySelector("meta[name='current_page_id']").getAttribute("content")

        }
      }]
    );
    window.snowplow('trackSiteSearch',
    	getUrlParamArray('q','')
    );

    function getUrlParamArray(param, defaultValue) {
    	var vars = [];
        var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        	if ( key === param ) {
        		vars.push(value);
        	}
        });
    	return vars;
    }
//  <!-- Snowplow stop plowing -->
