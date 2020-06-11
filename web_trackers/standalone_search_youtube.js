<!-- Snowplow starts plowing - Standalone vD.2.10.2 -->
<script src="https://www.youtube.com/iframe_api"></script>
<script>
// Each iFrame must have the JS Api enabled by appending 
// 'enablejsapi=1' to the src URL parameters. Ex:
// "https://www.youtube.com/embed/G9NL-ED0xdQ?enablejsapi=1"

// Gets called when the youtube player changes state, and sends
// and triggers a snowplow event with player status info.
function onPlayerStateChange(event) {
  var player_info = {
    status: '', 
    video_id: event.target.getVideoData().video_id,
    video_src: event.target.getVideoUrl(),
    title: event.target.getVideoData().title,
    author: event.target.getVideoData().author
  };
  
  switch(event.data) {
    case YT.PlayerState.PLAYING:
      player_info.status = 'Playing';
      track_youtube_player(player_info);
      break;
    case YT.PlayerState.PAUSED:
      player_info.status = 'Paused';
      track_youtube_player(player_info);
      break;
    case YT.PlayerState.ENDED:
      player_info.status = 'Ended';
      track_youtube_player(player_info);
      break;
    default:
      return;
  }
}

// Creates new youtube player object when the API loads.
function onYouTubeIframeAPIReady() {
  
  // Retrieve each iFrame by classname.
  // Replace "class-name" with your iFrame classname.
  var yt_players = Array.from(document.getElementsByClassName("class-name"));
  
  // Create a new Player object for each Player iframe 
  yt_players.forEach(function(item){
    player = new YT.Player(item.id, {
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
  })
}

// This gets called when the youtube player is ready.
function onPlayerReady(event) {
  var player_info = {
    status: 'Ready', 
    video_id: event.target.getVideoData().video_id,
    video_src: event.target.getVideoUrl(),
    title: event.target.getVideoData().title,
    author: event.target.getVideoData().author
  };
  track_youtube_player(player_info);
}

// Sends snowplow event with youtube player state.
function track_youtube_player(player_info) {
  window.snowplow('trackSelfDescribingEvent', {
    schema: "iglu:ca.bc.gov.youtube/youtube_playerstate/jsonschema/2-0-0",
    data: {
      status: player_info.status,
      video_src: player_info.video_src,
      video_id: player_info.video_id,
      title: player_info.title,
      author: player_info.author
    }
  });
}
</script>
<!-- Snowplow stop plowing -->

