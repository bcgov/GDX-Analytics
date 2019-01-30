// <!-- Snowplow starts plowing - Standalone v1.2.9.2 -->
;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
    p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
    };p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
    n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","https://sp-js.apps.gov.bc.ca/aubjyAzCUz7dJwqdbH3cMi45LjI.js","snowplow"));
var collector = 'spt.apps.gov.bc.ca';
window.snowplow('newTracker','rt',collector, {
    appId: "Snowplow_standalone",
    platform: 'web',
    respectDoNotTrack: true,
    post: true,
    forceSecureTracker: true,
    contexts: {
        webPage: true,
        performanceTiming: true
    }
});
window.snowplow('enableActivityTracking', 30, 30); // Ping every 30 seconds after 30 seconds
window.snowplow('enableLinkClickTracking');
window.snowplow('trackPageView');
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
//<!-- Snowplow stop plowing -->
