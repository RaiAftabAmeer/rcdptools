import React, { useState, useRef, useEffect } from 'react';
import './Card3D.css';

const Card3D = ({ data, index, onClick, viewType }) => {
  const [isHovered, setIsHovered] = useState(false);
  const cardRef = useRef(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const card = cardRef.current;
    if (!card) return;

    const handleMouseMove = (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = (y - centerY) / 10;
      const rotateY = (centerX - x) / 10;
      
      setMousePosition({ x: rotateX, y: rotateY });
    };

    const handleMouseLeave = () => {
      setMousePosition({ x: 0, y: 0 });
      setIsHovered(false);
    };

    const handleMouseEnter = () => {
      setIsHovered(true);
    };

    card.addEventListener('mousemove', handleMouseMove);
    card.addEventListener('mouseleave', handleMouseLeave);
    card.addEventListener('mouseenter', handleMouseEnter);

    return () => {
      card.removeEventListener('mousemove', handleMouseMove);
      card.removeEventListener('mouseleave', handleMouseLeave);
      card.removeEventListener('mouseenter', handleMouseEnter);
    };
  }, []);

  const cardStyle = {
    transform: `
      perspective(1000px)
      rotateX(${mousePosition.x}deg)
      rotateY(${mousePosition.y}deg)
      translateZ(${isHovered ? '20px' : '0px'})
      scale(${isHovered ? '1.05' : '1'})
    `,
    animationDelay: `${index * 0.1}s`
  };

  const getRecoveryStatus = () => {
    if (data.recoveryPercentage >= 80) return 'excellent';
    if (data.recoveryPercentage >= 60) return 'good';
    if (data.recoveryPercentage >= 40) return 'average';
    return 'poor';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div 
      ref={cardRef}
      className={`card-3d card-${getRecoveryStatus()} ${isHovered ? 'hovered' : ''}`}
      style={cardStyle}
      onClick={() => onClick(data)}
    >
      {/* Glow effect */}
      <div className="card-glow"></div>
      
      {/* Main card content */}
      <div className="card-content">
        {/* Header */}
        <div className="card-header">
          <h3 className="card-title">{data.key}</h3>
          <div className="card-subtitle">
            {viewType} • {data.activeCount} Clients
          </div>
        </div>

        {/* Main metrics */}
        <div className="card-metrics">
          <div className="metric-row">
            <div className="metric-item">
              <span className="metric-label">Recovery %</span>
              <span className={`metric-value recovery-${getRecoveryStatus()}`}>
                {data.recoveryPercentage}%
              </span>
            </div>
          </div>

          <div className="metric-row">
            <div className="metric-item">
              <span className="metric-label">Due Amount</span>
              <span className="metric-value">
                {formatCurrency(data.currentDueAmount)}
              </span>
            </div>
          </div>

          <div className="metric-row">
            <div className="metric-item">
              <span className="metric-label">Recovered</span>
              <span className="metric-value text-green">
                {formatCurrency(data.currentRecoveredAmount)}
              </span>
            </div>
          </div>

          <div className="metric-row">
            <div className="metric-item">
              <span className="metric-label">Clients</span>
              <span className="metric-value">
                {data.currentRecoveredClients}/{data.currentDueClients}
              </span>
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="progress-container">
          <div className="progress-label">Recovery Progress</div>
          <div className="progress-bar">
            <div 
              className={`progress-fill progress-${getRecoveryStatus()}`}
              style={{ width: `${Math.min(data.recoveryPercentage, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Additional stats */}
        <div className="card-stats">
          <div className="stat-item">
            <span className="stat-icon">💰</span>
            <span className="stat-text">Advance: {formatCurrency(data.currentAdvanceAmount)}</span>
          </div>
          <div className="stat-item">
            <span className="stat-icon">⏰</span>
            <span className="stat-text">Today: {data.todayRecoveredClients} clients</span>
          </div>
        </div>

        {/* Hover overlay */}
        <div className="card-overlay">
          <div className="overlay-content">
            <span className="overlay-icon">🔍</span>
            <span className="overlay-text">Click to view details</span>
          </div>
        </div>
      </div>

      {/* 3D border effects */}
      <div className="card-border-top"></div>
      <div className="card-border-bottom"></div>
      <div className="card-border-left"></div>
      <div className="card-border-right"></div>
      
      {/* Floating particles for visual effect */}
      {isHovered && (
        <div className="card-particles">
          {[...Array(6)].map((_, i) => (
            <div key={i} className={`particle particle-${i}`}></div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Card3D;