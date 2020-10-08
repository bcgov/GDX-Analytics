import React from 'react'
class SecondPage extends React.Component {
  render() {
    // <!-- Snowplow Track Page View -->
    window.snowplow('trackPageView');
    
    return <div><h1>Second Page</h1></div>
  }
}
export default SecondPage
