import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import { Route, Routes, Link, BrowserRouter as Router, BrowserRouter } from 'react-router-dom'
import App from './App'
import SecondPage from './SecondPage'
import Thirdpage from './ThirdPage'

const routing = (
  <BrowserRouter>
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
          <Routes>
            <Route exact path="/" element={<App />}></Route>
            <Route path="/secondPage" element={<SecondPage />}></Route>
            <Route path="/thirdPage" element={<Thirdpage />}></Route>
          </Routes>
    </div>
  </BrowserRouter>
)

ReactDOM.render(routing, document.getElementById('root'))
