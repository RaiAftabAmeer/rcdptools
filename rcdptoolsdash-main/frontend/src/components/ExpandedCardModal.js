import React, { useState } from 'react';
import './ExpandedCardModal.css';

const ExpandedCardModal = ({ data, viewType, onClose }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getRecoveryStatus = (percentage) => {
    if (percentage >= 80) return { class: 'excellent', text: 'Excellent' };
    if (percentage >= 60) return { class: 'good', text: 'Good' };
    if (percentage >= 40) return { class: 'average', text: 'Average' };
    return { class: 'poor', text: 'Poor' };
  };

  const sortedClients = [...data.clients].sort((a, b) => {
    let valueA = a[sortBy];
    let valueB = b[sortBy];
    
    if (typeof valueA === 'string') {
      valueA = valueA.toLowerCase();
      valueB = valueB.toLowerCase();
    }
    
    if (sortOrder === 'asc') {
      return valueA > valueB ? 1 : -1;
    } else {
      return valueA < valueB ? 1 : -1;
    }
  });

  const exportToExcel = () => {
    // Create CSV content for Excel export
    const headers = [
      'Sr No', 'Member ID', 'Name', 'CO', 'Branch', 
      'Due Total', 'Current Rec Total', 'Total Overdue', 
      'Current Advance', 'Opening Advance', 'OLP', 'Cell No'
    ];
    
    const csvContent = [
      headers.join(','),
      ...sortedClients.map(client => [
        client.srNo,
        client.memberId,
        `"${client.name}"`,
        `"${client.co}"`,
        `"${client.branch}"`,
        client.dueTotal,
        client.currentRecTotal,
        client.totalOverdue,
        client.currentAdvance,
        client.openingAdvance,
        client.olp,
        `"${client.cellNo}"`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${data.key}_client_details.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const recoveryStatus = getRecoveryStatus(data.recoveryPercentage);

  return (
    <div className="expanded-modal-overlay" onClick={onClose}>
      <div className="expanded-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="expanded-header">
          <div className="header-left">
            <h2 className="modal-title">{data.key}</h2>
            <div className="modal-subtitle">
              {viewType} • {data.activeCount} Active Clients
            </div>
          </div>
          <div className="header-right">
            <div className={`recovery-badge badge-${recoveryStatus.class}`}>
              {recoveryStatus.text} ({data.recoveryPercentage}%)
            </div>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'clients' ? 'active' : ''}`}
            onClick={() => setActiveTab('clients')}
          >
            Client Details ({data.clients.length})
          </button>
          <button 
            className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            Analytics
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="overview-tab">
              <div className="metrics-grid">
                <div className="metric-card">
                  <h4>Current Due</h4>
                  <div className="metric-value">{formatCurrency(data.currentDueAmount)}</div>
                  <div className="metric-detail">{data.currentDueClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Current Recovered</h4>
                  <div className="metric-value text-green">{formatCurrency(data.currentRecoveredAmount)}</div>
                  <div className="metric-detail">{data.currentRecoveredClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Last Month Till</h4>
                  <div className="metric-value">{formatCurrency(data.lastMonthTillAmount)}</div>
                  <div className="metric-detail">{data.lastMonthTillClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Remaining Due</h4>
                  <div className="metric-value text-red">{formatCurrency(data.remainingDueAmount)}</div>
                  <div className="metric-detail">{data.remainingDueClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Yesterday Recovered</h4>
                  <div className="metric-value">{formatCurrency(data.yesterdayRecoveredAmount)}</div>
                  <div className="metric-detail">{data.yesterdayRecoveredClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Today Recovered</h4>
                  <div className="metric-value text-blue">{formatCurrency(data.todayRecoveredAmount)}</div>
                  <div className="metric-detail">{data.todayRecoveredClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Current Advance</h4>
                  <div className="metric-value">{formatCurrency(data.currentAdvanceAmount)}</div>
                  <div className="metric-detail">{data.currentAdvanceClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>Opening Advance</h4>
                  <div className="metric-value">{formatCurrency(data.openingAdvanceAmount)}</div>
                  <div className="metric-detail">{data.openingAdvanceClients} clients</div>
                </div>
                
                <div className="metric-card">
                  <h4>OLP Amount</h4>
                  <div className="metric-value">{formatCurrency(data.olpAmount)}</div>
                  <div className="metric-detail">Total outstanding</div>
                </div>
              </div>
            </div>
          )}

          {/* Clients Tab */}
          {activeTab === 'clients' && (
            <div className="clients-tab">
              <div className="table-controls">
                <div className="sort-controls">
                  <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                    <option value="name">Name</option>
                    <option value="dueTotal">Due Total</option>
                    <option value="currentRecTotal">Current Recovered</option>
                    <option value="totalOverdue">Total Overdue</option>
                  </select>
                  <button 
                    className={`sort-btn ${sortOrder === 'asc' ? 'active' : ''}`}
                    onClick={() => setSortOrder('asc')}
                  >
                    ↑ Asc
                  </button>
                  <button 
                    className={`sort-btn ${sortOrder === 'desc' ? 'active' : ''}`}
                    onClick={() => setSortOrder('desc')}
                  >
                    ↓ Desc
                  </button>
                </div>
                <button className="export-btn" onClick={exportToExcel}>
                  📊 Export to Excel
                </button>
              </div>

              <div className="table-container">
                <table className="clients-table">
                  <thead>
                    <tr>
                      <th>Sr No</th>
                      <th>Member ID</th>
                      <th>Name</th>
                      <th>CO</th>
                      <th>Due Total</th>
                      <th>Current Rec</th>
                      <th>Overdue</th>
                      <th>Cell No</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedClients.map((client) => (
                      <tr key={client.memberId}>
                        <td>{client.srNo}</td>
                        <td>{client.memberId}</td>
                        <td className="name-cell">{client.name}</td>
                        <td>{client.co}</td>
                        <td className="amount-cell">{formatCurrency(client.dueTotal)}</td>
                        <td className="amount-cell text-green">{formatCurrency(client.currentRecTotal)}</td>
                        <td className="amount-cell text-red">{formatCurrency(client.totalOverdue)}</td>
                        <td>{client.cellNo}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="analytics-tab">
              <div className="analytics-grid">
                <div className="chart-card">
                  <h4>Recovery Performance</h4>
                  <div className="performance-indicator">
                    <div className="indicator-bar">
                      <div 
                        className={`indicator-fill fill-${recoveryStatus.class}`}
                        style={{ width: `${Math.min(data.recoveryPercentage, 100)}%` }}
                      ></div>
                    </div>
                    <div className="indicator-text">
                      {data.recoveryPercentage}% Recovery Rate
                    </div>
                  </div>
                </div>

                <div className="stats-card">
                  <h4>Key Statistics</h4>
                  <div className="stat-list">
                    <div className="stat-item">
                      <span>Active Clients:</span>
                      <span>{data.activeCount}</span>
                    </div>
                    <div className="stat-item">
                      <span>Due Clients:</span>
                      <span>{data.currentDueClients}</span>
                    </div>
                    <div className="stat-item">
                      <span>Recovered Clients:</span>
                      <span>{data.currentRecoveredClients}</span>
                    </div>
                    <div className="stat-item">
                      <span>Client Recovery Rate:</span>
                      <span>{data.currentDueClients > 0 ? Math.round((data.currentRecoveredClients / data.currentDueClients) * 100) : 0}%</span>
                    </div>
                  </div>
                </div>

                <div className="comparison-card">
                  <h4>Recovery Comparison</h4>
                  <div className="comparison-bars">
                    <div className="comparison-item">
                      <span>Current Month</span>
                      <div className="comparison-bar">
                        <div 
                          className="bar-fill current-month"
                          style={{ width: `${Math.min(data.recoveryPercentage, 100)}%` }}
                        ></div>
                      </div>
                      <span>{data.recoveryPercentage}%</span>
                    </div>
                    <div className="comparison-item">
                      <span>Last Month</span>
                      <div className="comparison-bar">
                        <div 
                          className="bar-fill last-month"
                          style={{ width: `${Math.min((data.lastMonthTillAmount / Math.max(data.currentDueAmount, 1)) * 100, 100)}%` }}
                        ></div>
                      </div>
                      <span>{data.currentDueAmount > 0 ? Math.round((data.lastMonthTillAmount / data.currentDueAmount) * 100) : 0}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExpandedCardModal;