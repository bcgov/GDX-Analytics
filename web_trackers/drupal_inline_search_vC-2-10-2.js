// <!-- Snowplow starts plowing - Standalone Search vB.2.10.2 -->
;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
    p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
    };p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
    n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","https://sp-js.apps.gov.bc.ca/MDWay3UqFnIiGVLIo7aoMi4xMC4y.js","snowplow"));
var collector = 'spm.gov.bc.ca';
window.snowplow('newTracker','rt',collector, {
    appId: "Snowplow_standalone",
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
window.snowplow('trackPageView');

if (window.location.pathname.split('/')[1] == 'search') {
    window.snowplow('trackSiteSearch', [decode_search(window.location.pathname.split('/')[2])]);
  }

  function decode_search(terms) {
    decoded = decodeURIComponent(terms);
    if ( decoded.indexOf('advanced;q=')  >= 0 ) {
      console.log(terms);
       // This will find the search terms parameter and parses the terms into an array.                                  
      decoded = decoded.split('bs=')[1].replace(/"/g,"").replace(/ OR/g,"").split(' ');
    }
    return decoded;
  }
//<!-- Snowplow stop plowing -->
