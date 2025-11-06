import React, { useState, useEffect } from 'react';
import { FiAlertCircle, FiAlertTriangle, FiCheckCircle, FiClock } from 'react-icons/fi';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import StatCard from '../components/StatCard';
import ErrorTable from '../components/ErrorTable';
import { statsAPI, errorLogsAPI } from '../services/api';
import './Dashboard.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [topErrors, setTopErrors] = useState([]);
  const [recentErrors, setRecentErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(7);

  useEffect(() => {
    loadDashboardData();
  }, [period]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, timelineRes, topErrorsRes, recentErrorsRes] = await Promise.all([
        statsAPI.getSummary(period),
        statsAPI.getTimeline(period),
        statsAPI.getTopErrors(5, period),
        errorLogsAPI.getAll({ limit: 10 })
      ]);

      setStats(statsRes.data);
      setTimeline(timelineRes.data);
      setTopErrors(topErrorsRes.data.top_errors);
      setRecentErrors(recentErrorsRes.data.errors);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const timelineChartData = timeline ? {
    labels: timeline.timeline.map(item => new Date(item.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })),
    datasets: [
      {
        label: 'Erros por dia',
        data: timeline.timeline.map(item => item.count),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      }
    ]
  } : null;

  const severityChartData = stats ? {
    labels: Object.keys(stats.by_severity),
    datasets: [
      {
        data: Object.values(stats.by_severity),
        backgroundColor: ['#10b981', '#f59e0b', '#f97316', '#ef4444'],
        borderWidth: 0,
      }
    ]
  } : null;

  const typeChartData = stats ? {
    labels: Object.keys(stats.by_type),
    datasets: [
      {
        label: 'Quantidade',
        data: Object.values(stats.by_type),
        backgroundColor: '#3b82f6',
      }
    ]
  } : null;

  if (loading) {
    return <div className="loading">Carregando dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1 className="page-title">Dashboard de Erros</h1>
        <div className="header-actions">
          <select 
            className="period-select"
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
          >
            <option value={1}>Último dia</option>
            <option value={7}>Últimos 7 dias</option>
            <option value={30}>Últimos 30 dias</option>
            <option value={90}>Últimos 90 dias</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4">
        <StatCard
          title="Total de Erros"
          value={stats?.total_errors || 0}
          icon={<FiAlertCircle />}
          color="primary"
          subtitle={`Últimos ${period} dias`}
        />
        <StatCard
          title="Erros Críticos"
          value={stats?.by_severity.CRITICAL || 0}
          icon={<FiAlertTriangle />}
          color="danger"
          subtitle="Requer atenção imediata"
        />
        <StatCard
          title="Erros Resolvidos"
          value={stats?.by_status.RESOLVED || 0}
          icon={<FiCheckCircle />}
          color="success"
          subtitle="Taxa de resolução"
        />
        <StatCard
          title="Taxa Diária"
          value={stats?.error_rate || 0}
          icon={<FiClock />}
          color="warning"
          subtitle="Erros por dia"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2" style={{ marginTop: '20px' }}>
        <div className="card">
          <h3 className="card-header">Timeline de Erros</h3>
          {timelineChartData && (
            <Line 
              data={timelineChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    display: false
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      stepSize: 1
                    }
                  }
                }
              }}
            />
          )}
        </div>

        <div className="card">
          <h3 className="card-header">Distribuição por Severidade</h3>
          {severityChartData && (
            <Doughnut 
              data={severityChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'bottom'
                  }
                }
              }}
            />
          )}
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3 className="card-header">Distribuição por Tipo de Erro</h3>
        {typeChartData && (
          <Bar 
            data={typeChartData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1
                  }
                }
              }
            }}
          />
        )}
      </div>

      {/* Top Errors */}
      <div className="card" style={{ marginTop: '20px' }}>
        <h3 className="card-header">Erros Mais Frequentes</h3>
        <div className="top-errors-list">
          {topErrors.map((error, index) => (
            <div key={index} className="top-error-item">
              <div className="top-error-rank">{index + 1}</div>
              <div className="top-error-content">
                <div className="top-error-message">{error.message}</div>
                <div className="top-error-type">{error.error_type}</div>
              </div>
              <div className="top-error-count">{error.count}x</div>
            </div>
          ))}
          {topErrors.length === 0 && (
            <div className="no-data">Nenhum erro registrado no período</div>
          )}
        </div>
      </div>

      {/* Recent Errors */}
      <div className="card" style={{ marginTop: '20px' }}>
        <h3 className="card-header">Erros Recentes</h3>
        <ErrorTable errors={recentErrors} loading={false} />
      </div>
    </div>
  );
};

export default Dashboard;

