import React from 'react';

class TrackPageView extends React.Component {
  componentDidMount() {
    if (window.snowplow) {
      window.snowplow('trackPageView');
    }
  }

  render() {
    return null; // nothing to render
  }
}

export default TrackPageView;
