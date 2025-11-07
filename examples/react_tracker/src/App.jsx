import React from 'react';
import TrackPageView from './TrackPageView.jsx';

class App extends React.Component {
  render() {
    return (
      <>
        <TrackPageView />
        <h1>Home</h1>
        <p>This is a single-page React app with Snowplow tracking.</p>
      </>
    );
  }
}

export default App;