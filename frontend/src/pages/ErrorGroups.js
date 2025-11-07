import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import './ErrorGroups.css';

const ErrorGroups = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    error_type: '',
    severity: '',
    source: '',
    status: ''
  });

  useEffect(() => {
    fetchGroups();
  }, [filters]);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.error_type) params.error_type = filters.error_type;
      if (filters.severity) params.severity = filters.severity;
      if (filters.source) params.source = filters.source;
      if (filters.status) params.status = filters.status;

      const response = await api.get('/groups', { params });
      setGroups(response.data.groups);
    } catch (error) {
      console.error('Error fetching groups:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const getSeverityColor = (severity) => {
    const colors = {
      LOW: '#4CAF50',
      MEDIUM: '#FFC107',
      HIGH: '#FF9800',
      CRITICAL: '#F44336'
    };
    return colors[severity] || '#999';
  };

  const getStatusBadge = (status) => {
    const badges = {
      OPEN: { text: 'Aberto', class: 'status-open' },
      IN_PROGRESS: { text: 'Em Progresso', class: 'status-in-progress' },
      RESOLVED: { text: 'Resolvido', class: 'status-resolved' },
      IGNORED: { text: 'Ignorado', class: 'status-ignored' }
    };
    return badges[status] || { text: status, class: '' };
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  };

  const getTimeSince = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} min atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    return `${diffDays}d atrás`;
  };

  return (
    <div className="error-groups-page">
      <div className="page-header">
        <h1>🔗 Grupos de Erros</h1>
        <p>Erros similares agrupados automaticamente usando fingerprinting</p>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Tipo:</label>
          <select name="error_type" value={filters.error_type} onChange={handleFilterChange}>
            <option value="">Todos</option>
            <option value="HTTP">HTTP</option>
            <option value="DATABASE">Database</option>
            <option value="AUTH">Auth</option>
            <option value="VALIDATION">Validation</option>
            <option value="PERFORMANCE">Performance</option>
            <option value="INTEGRATION">Integration</option>
            <option value="APPLICATION">Application</option>
            <option value="FRONTEND">Frontend</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Severidade:</label>
          <select name="severity" value={filters.severity} onChange={handleFilterChange}>
            <option value="">Todas</option>
            <option value="LOW">🟢 Low</option>
            <option value="MEDIUM">🟡 Medium</option>
            <option value="HIGH">🟠 High</option>
            <option value="CRITICAL">🔴 Critical</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Origem:</label>
          <select name="source" value={filters.source} onChange={handleFilterChange}>
            <option value="">Todas</option>
            <option value="frontend">Frontend</option>
            <option value="backend">Backend</option>
            <option value="database">Database</option>
            <option value="api">API</option>
            <option value="external_service">External Service</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Status:</label>
          <select name="status" value={filters.status} onChange={handleFilterChange}>
            <option value="">Todos</option>
            <option value="OPEN">Aberto</option>
            <option value="IN_PROGRESS">Em Progresso</option>
            <option value="RESOLVED">Resolvido</option>
            <option value="IGNORED">Ignorado</option>
          </select>
        </div>
      </div>

      {/* Groups List */}
      {loading ? (
        <div className="loading">Carregando grupos...</div>
      ) : (
        <div className="groups-container">
          {groups.length === 0 ? (
            <div className="no-groups">
              <p>Nenhum grupo de erros encontrado</p>
            </div>
          ) : (
            groups.map(group => (
              <Link to={`/groups/${group.id}`} key={group.id} className="group-card">
                <div className="group-header">
                  <div className="group-title">
                    <span 
                      className="severity-indicator" 
                      style={{ backgroundColor: getSeverityColor(group.severity) }}
                    />
                    <span className="error-type-badge">{group.error_type}</span>
                    <span className={`status-badge ${getStatusBadge(group.status).class}`}>
                      {getStatusBadge(group.status).text}
                    </span>
                  </div>
                  <div className="group-stats">
                    <span className="occurrences-badge">
                      {group.total_occurrences} ocorrências
                    </span>
                  </div>
                </div>

                <div className="group-message">
                  {group.message_pattern}
                </div>

                <div className="group-meta">
                  <div className="meta-item">
                    <span className="meta-label">Origem:</span>
                    <span className="meta-value">{group.source}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Primeira vez:</span>
                    <span className="meta-value">{formatDate(group.first_seen)}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Última vez:</span>
                    <span className="meta-value">
                      {getTimeSince(group.last_seen)}
                    </span>
                  </div>
                </div>

                {group.assigned_to && (
                  <div className="group-assigned">
                    👤 Atribuído a: {group.assigned_to}
                  </div>
                )}
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ErrorGroups;

