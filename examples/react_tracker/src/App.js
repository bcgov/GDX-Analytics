import React from 'react'

class App extends React.Component {
  render() {
    // <!-- Snowplow Track Page View -->
    window.snowplow('trackPageView');
    
    return (
      <div><script>window.snowplow('trackPageView');</script>
        <h1>Home</h1>
        <p>
          This is an example of a single page web app in react. It has the Snowplow Javascript Standalone web tracker vE.2.14.0 Installed.
        </p>
      </div>
    )
  }
}
export default App