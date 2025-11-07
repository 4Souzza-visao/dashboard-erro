import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Alerts.css';

const Alerts = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    condition: 'ERROR_COUNT',
    error_type: '',
    severity: '',
    source: '',
    condition_params: {
      threshold: 10,
      time_window_minutes: 5
    },
    notification_channels: [],
    notification_config: {},
    cooldown_minutes: 15,
    is_active: true
  });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await api.get('/alerts');
      setRules(response.data.rules);
    } catch (error) {
      console.error('Error fetching alert rules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingRule) {
        await api.patch(`/alerts/${editingRule.id}`, formData);
      } else {
        await api.post('/alerts', formData);
      }
      await fetchRules();
      resetForm();
    } catch (error) {
      console.error('Error saving alert rule:', error);
      alert('Erro ao salvar regra de alerta');
    }
  };

  const handleToggle = async (ruleId) => {
    try {
      await api.post(`/alerts/${ruleId}/toggle`);
      await fetchRules();
    } catch (error) {
      console.error('Error toggling alert rule:', error);
    }
  };

  const handleDelete = async (ruleId) => {
    if (!window.confirm('Tem certeza que deseja deletar esta regra?')) {
      return;
    }

    try {
      await api.delete(`/alerts/${ruleId}`);
      await fetchRules();
    } catch (error) {
      console.error('Error deleting alert rule:', error);
      alert('Erro ao deletar regra');
    }
  };

  const handleEdit = (rule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      description: rule.description || '',
      condition: rule.condition,
      error_type: rule.error_type || '',
      severity: rule.severity || '',
      source: rule.source || '',
      condition_params: rule.condition_params || {},
      notification_channels: rule.notification_channels || [],
      notification_config: rule.notification_config || {},
      cooldown_minutes: rule.cooldown_minutes,
      is_active: rule.is_active
    });
    setShowCreateForm(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      condition: 'ERROR_COUNT',
      error_type: '',
      severity: '',
      source: '',
      condition_params: {
        threshold: 10,
        time_window_minutes: 5
      },
      notification_channels: [],
      notification_config: {},
      cooldown_minutes: 15,
      is_active: true
    });
    setEditingRule(null);
    setShowCreateForm(false);
  };

  const handleChannelToggle = (channel) => {
    const channels = [...formData.notification_channels];
    const index = channels.indexOf(channel);
    
    if (index > -1) {
      channels.splice(index, 1);
    } else {
      channels.push(channel);
    }
    
    setFormData({ ...formData, notification_channels: channels });
  };

  const updateChannelConfig = (channel, key, value) => {
    const config = { ...formData.notification_config };
    if (!config[channel]) {
      config[channel] = {};
    }
    config[channel][key] = value;
    setFormData({ ...formData, notification_config: config });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Nunca';
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
  };

  const getConditionLabel = (condition) => {
    const labels = {
      ERROR_COUNT: 'Contagem de Erros',
      ERROR_RATE: 'Taxa de Erro',
      CRITICAL_ERROR: 'Erro Crítico',
      NEW_ERROR_TYPE: 'Novo Tipo de Erro',
      ERROR_SPIKE: 'Pico de Erros'
    };
    return labels[condition] || condition;
  };

  return (
    <div className="alerts-page">
      <div className="page-header">
        <div>
          <h1>🔔 Alertas e Notificações</h1>
          <p>Configure regras de alerta para ser notificado sobre erros críticos</p>
        </div>
        <button 
          className="btn-create" 
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          {showCreateForm ? '✕ Cancelar' : '+ Nova Regra'}
        </button>
      </div>

      {/* Create/Edit Form */}
      {showCreateForm && (
        <div className="alert-form-card">
          <h2>{editingRule ? 'Editar Regra' : 'Nova Regra de Alerta'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Nome da Regra *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="Ex: Alerta de Erros Críticos"
                />
              </div>

              <div className="form-group">
                <label>Condição *</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                  required
                >
                  <option value="ERROR_COUNT">Contagem de Erros</option>
                  <option value="ERROR_RATE">Taxa de Erro</option>
                  <option value="CRITICAL_ERROR">Erro Crítico</option>
                  <option value="NEW_ERROR_TYPE">Novo Tipo de Erro</option>
                  <option value="ERROR_SPIKE">Pico de Erros</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Descrição</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Descrição opcional da regra..."
                rows="3"
              />
            </div>

            <div className="form-section">
              <h3>Filtros (Opcional)</h3>
              <div className="form-row">
                <div className="form-group">
                  <label>Tipo de Erro</label>
                  <select
                    value={formData.error_type}
                    onChange={(e) => setFormData({ ...formData, error_type: e.target.value })}
                  >
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

                <div className="form-group">
                  <label>Severidade</label>
                  <select
                    value={formData.severity}
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  >
                    <option value="">Todas</option>
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Origem</label>
                  <input
                    type="text"
                    value={formData.source}
                    onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                    placeholder="Ex: backend, frontend"
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Parâmetros da Condição</h3>
              {formData.condition === 'ERROR_COUNT' && (
                <div className="form-row">
                  <div className="form-group">
                    <label>Limite de Erros</label>
                    <input
                      type="number"
                      value={formData.condition_params.threshold || 10}
                      onChange={(e) => setFormData({
                        ...formData,
                        condition_params: {
                          ...formData.condition_params,
                          threshold: parseInt(e.target.value)
                        }
                      })}
                      min="1"
                    />
                  </div>
                  <div className="form-group">
                    <label>Janela de Tempo (minutos)</label>
                    <input
                      type="number"
                      value={formData.condition_params.time_window_minutes || 5}
                      onChange={(e) => setFormData({
                        ...formData,
                        condition_params: {
                          ...formData.condition_params,
                          time_window_minutes: parseInt(e.target.value)
                        }
                      })}
                      min="1"
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="form-section">
              <h3>Canais de Notificação *</h3>
              <div className="channels-grid">
                {['SLACK', 'WEBHOOK', 'DISCORD', 'EMAIL'].map(channel => (
                  <div key={channel} className="channel-option">
                    <label>
                      <input
                        type="checkbox"
                        checked={formData.notification_channels.includes(channel)}
                        onChange={() => handleChannelToggle(channel)}
                      />
                      <span>{channel}</span>
                    </label>
                    
                    {formData.notification_channels.includes(channel) && (
                      <div className="channel-config">
                        <input
                          type="text"
                          placeholder={
                            channel === 'EMAIL' ? 'email@example.com' :
                            channel === 'SLACK' || channel === 'DISCORD' || channel === 'WEBHOOK' ? 'Webhook URL' :
                            'Destinatário'
                          }
                          value={formData.notification_config[channel]?.recipient || ''}
                          onChange={(e) => updateChannelConfig(channel, 'recipient', e.target.value)}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Cooldown (minutos)</label>
                <input
                  type="number"
                  value={formData.cooldown_minutes}
                  onChange={(e) => setFormData({ ...formData, cooldown_minutes: parseInt(e.target.value) })}
                  min="1"
                />
                <small>Tempo mínimo entre notificações</small>
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  <span>Regra ativa</span>
                </label>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-save">
                {editingRule ? 'Atualizar' : 'Criar'} Regra
              </button>
              <button type="button" className="btn-cancel" onClick={resetForm}>
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Rules List */}
      {loading ? (
        <div className="loading">Carregando regras...</div>
      ) : (
        <div className="rules-container">
          {rules.length === 0 ? (
            <div className="no-rules">
              <p>Nenhuma regra de alerta configurada</p>
              <button className="btn-create" onClick={() => setShowCreateForm(true)}>
                + Criar Primeira Regra
              </button>
            </div>
          ) : (
            rules.map(rule => (
              <div key={rule.id} className={`rule-card ${!rule.is_active ? 'inactive' : ''}`}>
                <div className="rule-header">
                  <div className="rule-title">
                    <h3>{rule.name}</h3>
                    <span className={`status-badge ${rule.is_active ? 'active' : 'inactive'}`}>
                      {rule.is_active ? '✓ Ativa' : '✕ Inativa'}
                    </span>
                  </div>
                  <div className="rule-actions">
                    <button 
                      className="btn-toggle" 
                      onClick={() => handleToggle(rule.id)}
                      title={rule.is_active ? 'Desativar' : 'Ativar'}
                    >
                      {rule.is_active ? '⏸' : '▶'}
                    </button>
                    <button 
                      className="btn-edit" 
                      onClick={() => handleEdit(rule)}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button 
                      className="btn-delete-small" 
                      onClick={() => handleDelete(rule.id)}
                      title="Deletar"
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                {rule.description && (
                  <p className="rule-description">{rule.description}</p>
                )}

                <div className="rule-details">
                  <div className="detail-item">
                    <strong>Condição:</strong> {getConditionLabel(rule.condition)}
                  </div>
                  {rule.error_type && (
                    <div className="detail-item">
                      <strong>Tipo:</strong> {rule.error_type}
                    </div>
                  )}
                  {rule.severity && (
                    <div className="detail-item">
                      <strong>Severidade:</strong> {rule.severity}
                    </div>
                  )}
                  <div className="detail-item">
                    <strong>Canais:</strong> {rule.notification_channels.join(', ')}
                  </div>
                  <div className="detail-item">
                    <strong>Cooldown:</strong> {rule.cooldown_minutes} min
                  </div>
                  <div className="detail-item">
                    <strong>Último disparo:</strong> {formatDate(rule.last_triggered)}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Alerts;

