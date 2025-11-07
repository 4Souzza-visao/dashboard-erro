import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiAlertCircle, FiActivity, FiLayers, FiBell } from 'react-icons/fi';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === path ? 'active' : '';
    }
    return location.pathname.startsWith(path) ? 'active' : '';
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
          <Link to="/groups" className={`nav-item ${isActive('/groups')}`}>
            <FiLayers />
            <span>Grupos de Erros</span>
          </Link>
          <Link to="/alerts" className={`nav-item ${isActive('/alerts')}`}>
            <FiBell />
            <span>Alertas</span>
          </Link>
        </nav>
        <div className="sidebar-footer">
          <p className="footer-text">v2.0.0</p>
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

