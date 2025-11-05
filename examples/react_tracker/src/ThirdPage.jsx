import React from 'react';

class ThirdPage extends React.Component {
  componentDidMount() {
    if (window.snowplow) {
      window.snowplow('trackPageView');
    }
  }

  render() {
    return (
      <div>
        <h1>Third Page</h1>
      </div>
    );
  }
}

export default ThirdPage;
