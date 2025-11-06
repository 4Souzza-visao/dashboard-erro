import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ErrorList from './pages/ErrorList';
import ErrorDetail from './pages/ErrorDetail';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/errors" element={<ErrorList />} />
          <Route path="/errors/:id" element={<ErrorDetail />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;

