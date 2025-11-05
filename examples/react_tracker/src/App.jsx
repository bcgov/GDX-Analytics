import React from 'react';

class App extends React.Component {
  componentDidMount() {
    // Track a page view once the component has mounted
    if (window.snowplow) {
      window.snowplow('trackPageView');
    }
  }

  render() {
    return (
      <div>
        <h1>Home</h1>
        <p>
          This is an example of a single-page web app in React.
          It has the Snowplow JavaScript Standalone web tracker vE.2.14.0 installed.
        </p>
      </div>
    );
  }
}

export default App;