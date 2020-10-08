import React from 'react'
class ThirdPage extends React.Component {
  render() {
    // <!-- Snowplow Track Page View -->
    window.snowplow('trackPageView');
    
    return <h1>Third Page</h1>
  }
}
export default ThirdPage