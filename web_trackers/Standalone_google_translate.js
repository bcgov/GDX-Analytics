// <!-- Snowplow starts plowing - Standalone vE.2.14.0 -->
;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
 p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
 };p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
 n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","https://www2.gov.bc.ca/StaticWebResources/static/sp/sp-2-14-0.js","snowplow"));
var collector = 'spm.apps.gov.bc.ca';
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

// Track Google Translate Widget on translate
window.addEventListener('change', function(event) {
  if(event.target.className === 'goog-te-combo'){
    setTimeout(
      window.snowplow('trackSelfDescribingEvent', {
        schema: 'iglu:ca.bc.gov.googtrans/google_translate/jsonschema/1-0-0',
        data: {
          translation_data: String(document.cookie).match(/googtrans=\/[a-z]{2,5}\/[^;]{2,5}/)[0]
      }
    }),
    500);
  }
});
 
// Track Google Translation Widget on Page Views
window.addEventListener('load', function(event) {
  window.snowplow('trackSelfDescribingEvent', {
    schema: 'iglu:ca.bc.gov.googtrans/google_translate/jsonschema/1-0-0',
    data: {
      translation_data: String(document.cookie).match(/googtrans=\/[a-z]{2,5}\/[^;]{2,5}/)[0]
    }
  });
});
//<!-- Snowplow stop plowing -->
