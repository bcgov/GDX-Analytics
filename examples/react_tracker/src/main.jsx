import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import App from './App.jsx';
import SecondPage from './SecondPage.jsx';
import ThirdPage from './ThirdPage.jsx';

ReactDOM.render(
  <BrowserRouter>
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
  </BrowserRouter>,
  document.getElementById('root')
);