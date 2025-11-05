import React from 'react';

class SecondPage extends React.Component {
  componentDidMount() {
    // Track page view once when the page loads
    if (window.snowplow) {
      window.snowplow('trackPageView');
    }
  }

  render() {
    return (
      <div>
        <h1>Second Page</h1>
      </div>
    );
  }
}

export default SecondPage;
