import React from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import './ErrorTable.css';

const getSeverityColor = (severity) => {
  const colors = {
    LOW: '#10b981',
    MEDIUM: '#f59e0b',
    HIGH: '#f97316',
    CRITICAL: '#ef4444'
  };
  return colors[severity] || '#6b7280';
};

const getStatusColor = (status) => {
  const colors = {
    OPEN: '#ef4444',
    IN_PROGRESS: '#f59e0b',
    RESOLVED: '#10b981',
    IGNORED: '#6b7280'
  };
  return colors[status] || '#6b7280';
};

const ErrorTable = ({ errors, loading }) => {
  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  if (!errors || errors.length === 0) {
    return <div className="no-data">Nenhum erro encontrado</div>;
  }

  return (
    <div className="table-container">
      <table className="error-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Mensagem</th>
            <th>Tipo</th>
            <th>Severidade</th>
            <th>Origem</th>
            <th>Status</th>
            <th>Data/Hora</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {errors.map((error) => (
            <tr key={error.id}>
              <td className="td-id">#{error.id}</td>
              <td className="td-message">
                <div className="message-cell">
                  <span className="message-text" title={error.message}>
                    {error.message}
                  </span>
                  {error.endpoint && (
                    <span className="endpoint-badge">{error.method} {error.endpoint}</span>
                  )}
                </div>
              </td>
              <td>
                <span className="type-badge">{error.error_type}</span>
              </td>
              <td>
                <span 
                  className="severity-badge"
                  style={{ backgroundColor: getSeverityColor(error.severity) }}
                >
                  {error.severity}
                </span>
              </td>
              <td className="td-source">{error.source}</td>
              <td>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(error.status) }}
                >
                  {error.status}
                </span>
              </td>
              <td className="td-date">
                {format(new Date(error.timestamp), 'dd/MM/yyyy HH:mm', { locale: ptBR })}
              </td>
              <td>
                <Link to={`/errors/${error.id}`} className="btn-view">
                  Ver Detalhes
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ErrorTable;

