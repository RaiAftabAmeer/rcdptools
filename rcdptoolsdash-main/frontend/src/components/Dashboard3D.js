import React, { useState, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import Card3D from './Card3D';
import StarField from './StarField';
import FileUploadModal from './FileUploadModal';
import ExpandedCardModal from './ExpandedCardModal';
import './Dashboard3D.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard3D = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [viewType, setViewType] = useState('Branch'); // 'Branch' or 'CO'
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [expandedCard, setExpandedCard] = useState(null);
  const [error, setError] = useState('');

  // Load existing dashboard data on component mount
  useEffect(() => {
    loadExistingData();
  }, []);

  const loadExistingData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard-data`);
      setDashboardData(response.data);
    } catch (error) {
      console.log('No existing dashboard data found');
    }
  };

  const handleFileUpload = async (files, dates) => {
    if (!files.currentMonth || !files.lastMonth) {
      setError('Please select both current month and last month files');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('current_month_file', files.currentMonth);
    formData.append('last_month_file', files.lastMonth);
    formData.append('yesterday_date', dates.yesterday || '');
    formData.append('today_date', dates.today || '');

    try {
      const response = await axios.post(`${API}/upload-excel`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDashboardData(response.data);
      setShowUploadModal(false);
    } catch (error) {
      console.error('Error uploading files:', error);
      setError(error.response?.data?.detail || 'Error uploading files');
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = (cardData) => {
    setExpandedCard(cardData);
  };

  const getCurrentMetrics = () => {
    if (!dashboardData) return [];
    return viewType === 'Branch' ? dashboardData.branchMetrics : dashboardData.coMetrics;
  };

  const getTotalMetrics = () => {
    if (!dashboardData) return null;
    return dashboardData.totalMetrics;
  };

  return (
    <div className="dashboard-3d">
      {/* Animated Star Field Background */}
      <StarField />
      
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">
            RCDP Recovery Status Dashboard
          </h1>
          <p className="dashboard-subtitle">
            3D Interactive Analytics Platform
          </p>
          
          {/* Control Panel */}
          <div className="control-panel">
            <button 
              className="upload-btn"
              onClick={() => setShowUploadModal(true)}
            >
              <span className="btn-icon">📊</span>
              Upload Excel Files
            </button>
            
            <div className="view-toggle">
              <button 
                className={`toggle-btn ${viewType === 'Branch' ? 'active' : ''}`}
                onClick={() => setViewType('Branch')}
              >
                Branch View
              </button>
              <button 
                className={`toggle-btn ${viewType === 'CO' ? 'active' : ''}`}
                onClick={() => setViewType('CO')}
              >
                CO View
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Total Metrics Summary */}
      {getTotalMetrics() && (
        <div className="metrics-summary">
          <div className="summary-card">
            <h3>Total Active Clients</h3>
            <div className="metric-value">{getTotalMetrics().totalActiveClients}</div>
          </div>
          <div className="summary-card">
            <h3>Total Due Amount</h3>
            <div className="metric-value">{getTotalMetrics().totalCurrentDueAmount.toFixed(2)}</div>
          </div>
          <div className="summary-card">
            <h3>Total Recovered</h3>
            <div className="metric-value">{getTotalMetrics().totalCurrentRecoveredAmount.toFixed(2)}</div>
          </div>
          <div className="summary-card">
            <h3>Recovery Percentage</h3>
            <div className="metric-value">{getTotalMetrics().totalRecoveryPercentage}%</div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Processing Excel files...</p>
          </div>
        </div>
      )}

      {/* 3D Cards Grid */}
      <div className="cards-container">
        {getCurrentMetrics().length > 0 ? (
          <div className="cards-grid">
            {getCurrentMetrics().map((metric, index) => (
              <Card3D
                key={metric.key}
                data={metric}
                index={index}
                onClick={() => handleCardClick(metric)}
                viewType={viewType}
              />
            ))}
          </div>
        ) : (
          <div className="no-data-message">
            <div className="no-data-content">
              <h3>No Data Available</h3>
              <p>Upload Excel files to view the 3D dashboard</p>
              <button 
                className="upload-btn-large"
                onClick={() => setShowUploadModal(true)}
              >
                Upload Files
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showUploadModal && (
        <FileUploadModal
          onUpload={handleFileUpload}
          onClose={() => setShowUploadModal(false)}
          loading={loading}
        />
      )}

      {expandedCard && (
        <ExpandedCardModal
          data={expandedCard}
          viewType={viewType}
          onClose={() => setExpandedCard(null)}
        />
      )}
    </div>
  );
};

export default Dashboard3D;