import React, { useState, useEffect } from 'react';
import { FiFilter, FiRefreshCw, FiSearch } from 'react-icons/fi';
import ErrorTable from '../components/ErrorTable';
import { errorLogsAPI } from '../services/api';
import './ErrorList.css';

const ErrorList = () => {
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    error_type: '',
    severity: '',
    source: '',
    status: '',
    search: ''
  });
  const [pagination, setPagination] = useState({
    total: 0,
    skip: 0,
    limit: 50
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadErrors();
  }, [filters, pagination.skip]);

  const loadErrors = async () => {
    setLoading(true);
    try {
      const params = {
        skip: pagination.skip,
        limit: pagination.limit,
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v !== '')
        )
      };

      const response = await errorLogsAPI.getAll(params);
      setErrors(response.data.errors);
      setPagination(prev => ({
        ...prev,
        total: response.data.total
      }));
    } catch (error) {
      console.error('Error loading errors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPagination(prev => ({ ...prev, skip: 0 }));
  };

  const clearFilters = () => {
    setFilters({
      error_type: '',
      severity: '',
      source: '',
      status: '',
      search: ''
    });
  };

  const handlePageChange = (newSkip) => {
    setPagination(prev => ({ ...prev, skip: newSkip }));
  };

  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1;

  return (
    <div className="error-list-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Logs de Erros</h1>
          <p className="page-subtitle">
            Total de {pagination.total} erro{pagination.total !== 1 ? 's' : ''} encontrado{pagination.total !== 1 ? 's' : ''}
          </p>
        </div>
        <div className="header-actions">
          <button 
            className="btn btn-outline"
            onClick={() => setShowFilters(!showFilters)}
          >
            <FiFilter /> Filtros
          </button>
          <button 
            className="btn btn-primary"
            onClick={loadErrors}
          >
            <FiRefreshCw /> Atualizar
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="filters-panel">
          <div className="filters-grid">
            <div className="filter-group">
              <label>Buscar</label>
              <div className="search-input">
                <FiSearch />
                <input
                  type="text"
                  placeholder="Buscar por mensagem..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
              </div>
            </div>

            <div className="filter-group">
              <label>Tipo de Erro</label>
              <select
                value={filters.error_type}
                onChange={(e) => handleFilterChange('error_type', e.target.value)}
              >
                <option value="">Todos</option>
                <option value="HTTP">HTTP</option>
                <option value="DATABASE">Database</option>
                <option value="AUTH">Autenticação</option>
                <option value="VALIDATION">Validação</option>
                <option value="PERFORMANCE">Performance</option>
                <option value="INTEGRATION">Integração</option>
                <option value="APPLICATION">Aplicação</option>
                <option value="FRONTEND">Frontend</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Severidade</label>
              <select
                value={filters.severity}
                onChange={(e) => handleFilterChange('severity', e.target.value)}
              >
                <option value="">Todas</option>
                <option value="LOW">Baixa</option>
                <option value="MEDIUM">Média</option>
                <option value="HIGH">Alta</option>
                <option value="CRITICAL">Crítica</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Origem</label>
              <select
                value={filters.source}
                onChange={(e) => handleFilterChange('source', e.target.value)}
              >
                <option value="">Todas</option>
                <option value="frontend">Frontend</option>
                <option value="backend">Backend</option>
                <option value="database">Database</option>
                <option value="api">API</option>
                <option value="external_service">Serviço Externo</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Status</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <option value="">Todos</option>
                <option value="OPEN">Aberto</option>
                <option value="IN_PROGRESS">Em Progresso</option>
                <option value="RESOLVED">Resolvido</option>
                <option value="IGNORED">Ignorado</option>
              </select>
            </div>

            <div className="filter-group">
              <button className="btn btn-outline" onClick={clearFilters}>
                Limpar Filtros
              </button>
            </div>
          </div>
        </div>
      )}

      <ErrorTable errors={errors} loading={loading} />

      {!loading && pagination.total > pagination.limit && (
        <div className="pagination">
          <button
            className="btn btn-outline"
            disabled={currentPage === 1}
            onClick={() => handlePageChange((currentPage - 2) * pagination.limit)}
          >
            Anterior
          </button>
          <span className="pagination-info">
            Página {currentPage} de {totalPages}
          </span>
          <button
            className="btn btn-outline"
            disabled={currentPage === totalPages}
            onClick={() => handlePageChange(currentPage * pagination.limit)}
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  );
};

export default ErrorList;

