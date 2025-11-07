import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import './GroupDetail.css';

const GroupDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [group, setGroup] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [updateData, setUpdateData] = useState({
    status: '',
    assigned_to: '',
    notes: ''
  });

  useEffect(() => {
    fetchGroupDetails();
  }, [id]);

  const fetchGroupDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/groups/${id}`);
      setGroup(response.data);
      setUpdateData({
        status: response.data.status,
        assigned_to: response.data.assigned_to || '',
        notes: response.data.notes || ''
      });
    } catch (error) {
      console.error('Error fetching group details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      setUpdating(true);
      await api.patch(`/groups/${id}`, updateData);
      await fetchGroupDetails();
      setShowUpdateForm(false);
    } catch (error) {
      console.error('Error updating group:', error);
      alert('Erro ao atualizar grupo');
    } finally {
      setUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Tem certeza que deseja deletar este grupo e todos os erros associados?')) {
      return;
    }

    try {
      await api.delete(`/groups/${id}`);
      navigate('/groups');
    } catch (error) {
      console.error('Error deleting group:', error);
      alert('Erro ao deletar grupo');
    }
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

  if (loading) {
    return <div className="loading">Carregando detalhes do grupo...</div>;
  }

  if (!group) {
    return <div className="error-message">Grupo não encontrado</div>;
  }

  return (
    <div className="group-detail-page">
      <div className="page-header">
        <Link to="/groups" className="back-button">← Voltar para Grupos</Link>
        <h1>Detalhes do Grupo #{group.id}</h1>
      </div>

      <div className="group-info-card">
        <div className="info-header">
          <div className="info-title">
            <span 
              className="severity-indicator" 
              style={{ backgroundColor: getSeverityColor(group.severity) }}
            />
            <span className="error-type-badge">{group.error_type}</span>
            <span className={`status-badge ${getStatusBadge(group.status).class}`}>
              {getStatusBadge(group.status).text}
            </span>
          </div>
          <div className="info-actions">
            <button 
              className="btn-update" 
              onClick={() => setShowUpdateForm(!showUpdateForm)}
            >
              ✏️ Editar
            </button>
            <button className="btn-delete" onClick={handleDelete}>
              🗑️ Deletar
            </button>
          </div>
        </div>

        <div className="group-message">
          <h3>Mensagem Padrão:</h3>
          <p>{group.message_pattern}</p>
        </div>

        <div className="group-stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total de Ocorrências</div>
            <div className="stat-value">{group.total_occurrences}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Origem</div>
            <div className="stat-value">{group.source}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Primeira Ocorrência</div>
            <div className="stat-value">{formatDate(group.first_seen)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Última Ocorrência</div>
            <div className="stat-value">{formatDate(group.last_seen)}</div>
          </div>
        </div>

        <div className="fingerprint-section">
          <h4>Fingerprint:</h4>
          <code>{group.fingerprint}</code>
        </div>

        {group.assigned_to && (
          <div className="assigned-section">
            <strong>👤 Atribuído a:</strong> {group.assigned_to}
          </div>
        )}

        {group.notes && (
          <div className="notes-section">
            <strong>📝 Notas:</strong>
            <p>{group.notes}</p>
          </div>
        )}
      </div>

      {/* Update Form */}
      {showUpdateForm && (
        <div className="update-form-card">
          <h3>Atualizar Grupo</h3>
          <form onSubmit={handleUpdate}>
            <div className="form-group">
              <label>Status:</label>
              <select
                value={updateData.status}
                onChange={(e) => setUpdateData({ ...updateData, status: e.target.value })}
              >
                <option value="OPEN">Aberto</option>
                <option value="IN_PROGRESS">Em Progresso</option>
                <option value="RESOLVED">Resolvido</option>
                <option value="IGNORED">Ignorado</option>
              </select>
            </div>

            <div className="form-group">
              <label>Atribuído a:</label>
              <input
                type="text"
                value={updateData.assigned_to}
                onChange={(e) => setUpdateData({ ...updateData, assigned_to: e.target.value })}
                placeholder="Nome do responsável"
              />
            </div>

            <div className="form-group">
              <label>Notas:</label>
              <textarea
                value={updateData.notes}
                onChange={(e) => setUpdateData({ ...updateData, notes: e.target.value })}
                placeholder="Adicione notas sobre este grupo de erros..."
                rows="4"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-save" disabled={updating}>
                {updating ? 'Salvando...' : 'Salvar'}
              </button>
              <button 
                type="button" 
                className="btn-cancel" 
                onClick={() => setShowUpdateForm(false)}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Recent Errors */}
      <div className="recent-errors-section">
        <h2>Erros Recentes (últimos 10)</h2>
        {group.recent_errors && group.recent_errors.length > 0 ? (
          <div className="errors-list">
            {group.recent_errors.map(error => (
              <Link to={`/errors/${error.id}`} key={error.id} className="error-item">
                <div className="error-header">
                  <span className="error-id">#{error.id}</span>
                  <span className="error-timestamp">{formatDate(error.timestamp)}</span>
                </div>
                <div className="error-message">{error.message}</div>
                {error.endpoint && (
                  <div className="error-endpoint">
                    <strong>{error.method}</strong> {error.endpoint}
                  </div>
                )}
              </Link>
            ))}
          </div>
        ) : (
          <p className="no-errors">Nenhum erro encontrado neste grupo</p>
        )}
      </div>
    </div>
  );
};

export default GroupDetail;

