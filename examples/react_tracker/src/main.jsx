import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import App from './App';
import SecondPage from './SecondPage';
import ThirdPage from './ThirdPage';

const routing = (
  <BrowserRouter>
    <div>
      <nav>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/secondPage">Second Page</Link></li>
          <li><Link to="/thirdPage">Third Page</Link></li>
        </ul>
      </nav>

      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/secondPage" element={<SecondPage />} />
        <Route path="/thirdPage" element={<ThirdPage />} />
      </Routes>
    </div>
  </BrowserRouter>
);

ReactDOM.render(routing, document.getElementById('root'));