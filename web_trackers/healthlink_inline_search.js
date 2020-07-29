// <!-- Snowplow starts plowing - Healthlink Inline Search vC.2.10.2 -->
;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
    p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
    };p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
    n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","https://www2.gov.bc.ca/StaticWebResources/static/sp/sp-2-14-0.js","snowplow"));
var collector = 'spm.gov.bc.ca';
window.snowplow('newTracker','rt',collector, {
    appId: "Snowplow_standalone",
    cookieLifetime: 86400 * 548,
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

if (window.location.pathname.split('/')[1] == 'search'
    && window.location.pathname != "/search"
) {
    window.snowplow('trackSiteSearch', [decode_search(window.location.pathname.split('/')[2])]);
}

  function decode_search(encoded_terms) {
    terms = decodeURIComponent(encoded_terms);
    if (terms.indexOf('bs=')  >= 0) {
       // This will find the search terms parameter and parses the terms into an array.                                  
      terms = terms.split('bs=')[1].replace(/ OR/g,"");
    }
    terms = terms.replace('+', " ").replace(/"/g,"").replace(/,/g,"");
    return terms;
  }
//<!-- Snowplow stop plowing -->
