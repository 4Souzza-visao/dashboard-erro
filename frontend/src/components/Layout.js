import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiAlertCircle, FiActivity } from 'react-icons/fi';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <FiActivity className="logo-icon" />
          <h1 className="sidebar-title">Error Dashboard</h1>
        </div>
        <nav className="sidebar-nav">
          <Link to="/" className={`nav-item ${isActive('/')}`}>
            <FiHome />
            <span>Dashboard</span>
          </Link>
          <Link to="/errors" className={`nav-item ${isActive('/errors')}`}>
            <FiAlertCircle />
            <span>Logs de Erros</span>
          </Link>
        </nav>
        <div className="sidebar-footer">
          <p className="footer-text">v1.0.0</p>
          <p className="footer-text">© 2024 Error Dashboard</p>
        </div>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;

