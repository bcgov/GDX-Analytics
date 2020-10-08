import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import { Route, Link, BrowserRouter as Router } from 'react-router-dom'
import App from './App'
import SecondPage from './SecondPage'
import Thirdpage from './ThirdPage'

const routing = (
  <Router>
    <div>
      <ul>
        <li>
          <Link to="/">Home</Link>
        </li>
        <li>
          <Link to="/secondPage">Second Page</Link>
        </li>
        <li>
          <Link to="/thirdPage">Third Page</Link>
        </li>
      </ul>
      <Route exact path="/" component={App} />
      <Route path="/secondPage" component={SecondPage} />
      <Route path="/thirdPage" component={Thirdpage} />
    </div>
  </Router>
)

ReactDOM.render(routing, document.getElementById('root'))
