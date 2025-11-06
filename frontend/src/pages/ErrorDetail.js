import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiUser, FiGlobe, FiCode, FiTag } from 'react-icons/fi';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { errorLogsAPI } from '../services/api';
import './ErrorDetail.css';

const ErrorDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [status, setStatus] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    loadError();
  }, [id]);

  const loadError = async () => {
    setLoading(true);
    try {
      const response = await errorLogsAPI.getById(id);
      setError(response.data);
      setStatus(response.data.status);
      setNotes(response.data.notes || '');
    } catch (error) {
      console.error('Error loading error details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async () => {
    setUpdating(true);
    try {
      await errorLogsAPI.update(id, { status, notes: notes || null });
      await loadError();
      alert('Status atualizado com sucesso!');
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Erro ao atualizar status');
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Tem certeza que deseja deletar este erro?')) {
      return;
    }

    try {
      await errorLogsAPI.delete(id);
      alert('Erro deletado com sucesso!');
      navigate('/errors');
    } catch (error) {
      console.error('Error deleting error:', error);
      alert('Erro ao deletar');
    }
  };

  if (loading) {
    return <div className="loading">Carregando detalhes...</div>;
  }

  if (!error) {
    return <div className="error-message">Erro não encontrado</div>;
  }

  const getSeverityColor = (severity) => {
    const colors = {
      LOW: '#10b981',
      MEDIUM: '#f59e0b',
      HIGH: '#f97316',
      CRITICAL: '#ef4444'
    };
    return colors[severity] || '#6b7280';
  };

  return (
    <div className="error-detail-page">
      <button className="btn btn-outline back-button" onClick={() => navigate('/errors')}>
        <FiArrowLeft /> Voltar
      </button>

      <div className="error-detail-header">
        <div className="error-detail-title">
          <h1>Erro #{error.id}</h1>
          <div className="error-badges">
            <span 
              className="badge severity-badge"
              style={{ backgroundColor: getSeverityColor(error.severity) }}
            >
              {error.severity}
            </span>
            <span className="badge type-badge">{error.error_type}</span>
            <span className="badge source-badge">{error.source}</span>
          </div>
        </div>
      </div>

      <div className="error-detail-grid">
        <div className="error-detail-main">
          <div className="card">
            <h3 className="card-header">Mensagem do Erro</h3>
            <p className="error-message-text">{error.message}</p>
          </div>

          {error.stack_trace && (
            <div className="card">
              <h3 className="card-header">
                <FiCode /> Stack Trace
              </h3>
              <pre className="stack-trace">{error.stack_trace}</pre>
            </div>
          )}

          {error.metadata && Object.keys(error.metadata).length > 0 && (
            <div className="card">
              <h3 className="card-header">
                <FiTag /> Metadados
              </h3>
              <pre className="metadata">{JSON.stringify(error.metadata, null, 2)}</pre>
            </div>
          )}

          <div className="card">
            <h3 className="card-header">Atualizar Status</h3>
            <div className="status-form">
              <div className="form-group">
                <label>Status</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="form-control"
                >
                  <option value="OPEN">Aberto</option>
                  <option value="IN_PROGRESS">Em Progresso</option>
                  <option value="RESOLVED">Resolvido</option>
                  <option value="IGNORED">Ignorado</option>
                </select>
              </div>

              <div className="form-group">
                <label>Notas</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="form-control"
                  rows="4"
                  placeholder="Adicione notas sobre este erro..."
                />
              </div>

              <div className="form-actions">
                <button
                  className="btn btn-primary"
                  onClick={handleUpdateStatus}
                  disabled={updating}
                >
                  {updating ? 'Salvando...' : 'Salvar Alterações'}
                </button>
                <button
                  className="btn btn-danger"
                  onClick={handleDelete}
                >
                  Deletar Erro
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="error-detail-sidebar">
          <div className="card">
            <h3 className="card-header">Informações</h3>
            <div className="info-list">
              <div className="info-item">
                <FiClock className="info-icon" />
                <div>
                  <div className="info-label">Timestamp</div>
                  <div className="info-value">
                    {format(new Date(error.timestamp), "dd/MM/yyyy 'às' HH:mm:ss", { locale: ptBR })}
                  </div>
                </div>
              </div>

              {error.endpoint && (
                <div className="info-item">
                  <FiCode className="info-icon" />
                  <div>
                    <div className="info-label">Endpoint</div>
                    <div className="info-value mono">{error.method} {error.endpoint}</div>
                  </div>
                </div>
              )}

              {error.status_code && (
                <div className="info-item">
                  <FiTag className="info-icon" />
                  <div>
                    <div className="info-label">Status Code</div>
                    <div className="info-value">{error.status_code}</div>
                  </div>
                </div>
              )}

              {error.user_id && (
                <div className="info-item">
                  <FiUser className="info-icon" />
                  <div>
                    <div className="info-label">User ID</div>
                    <div className="info-value">{error.user_id}</div>
                  </div>
                </div>
              )}

              {error.ip_address && (
                <div className="info-item">
                  <FiGlobe className="info-icon" />
                  <div>
                    <div className="info-label">IP Address</div>
                    <div className="info-value mono">{error.ip_address}</div>
                  </div>
                </div>
              )}

              {error.user_agent && (
                <div className="info-item">
                  <FiGlobe className="info-icon" />
                  <div>
                    <div className="info-label">User Agent</div>
                    <div className="info-value small">{error.user_agent}</div>
                  </div>
                </div>
              )}

              {error.resolved_at && (
                <div className="info-item">
                  <FiClock className="info-icon" />
                  <div>
                    <div className="info-label">Resolvido em</div>
                    <div className="info-value">
                      {format(new Date(error.resolved_at), "dd/MM/yyyy 'às' HH:mm:ss", { locale: ptBR })}
                    </div>
                  </div>
                </div>
              )}

              <div className="info-item">
                <div>
                  <div className="info-label">Ocorrências</div>
                  <div className="info-value">{error.occurrences}x</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorDetail;

