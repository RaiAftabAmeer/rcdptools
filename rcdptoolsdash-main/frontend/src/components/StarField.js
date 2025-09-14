import React, { useEffect, useRef } from 'react';
import './StarField.css';

const StarField = () => {
  const starsRef = useRef(null);

  useEffect(() => {
    const generateStars = () => {
      const container = starsRef.current;
      if (!container) return;

      // Clear existing stars
      container.innerHTML = '';

      // Create different layers of stars
      const starLayers = [
        { count: 100, size: 1, opacity: 0.8, speed: 0.5 },
        { count: 50, size: 2, opacity: 0.6, speed: 0.3 },
        { count: 30, size: 3, opacity: 0.4, speed: 0.2 }
      ];

      starLayers.forEach((layer, layerIndex) => {
        for (let i = 0; i < layer.count; i++) {
          const star = document.createElement('div');
          star.className = `star star-layer-${layerIndex}`;
          
          // Random position
          const x = Math.random() * 100;
          const y = Math.random() * 100;
          
          // Random animation delay for twinkling
          const twinkleDelay = Math.random() * 3;
          
          star.style.cssText = `
            left: ${x}%;
            top: ${y}%;
            width: ${layer.size}px;
            height: ${layer.size}px;
            opacity: ${layer.opacity};
            animation-delay: ${twinkleDelay}s;
            animation-duration: ${2 + Math.random() * 2}s;
          `;
          
          container.appendChild(star);
        }
      });

      // Create shooting stars occasionally
      setInterval(() => {
        if (Math.random() < 0.3) { // 30% chance every interval
          createShootingStar();
        }
      }, 3000);
    };

    const createShootingStar = () => {
      const container = starsRef.current;
      if (!container) return;

      const shootingStar = document.createElement('div');
      shootingStar.className = 'shooting-star';
      
      // Random starting position (from edges)
      const startFromTop = Math.random() < 0.5;
      const startX = startFromTop ? Math.random() * 100 : (Math.random() < 0.5 ? -5 : 105);
      const startY = startFromTop ? -5 : Math.random() * 100;
      
      shootingStar.style.cssText = `
        left: ${startX}%;
        top: ${startY}%;
      `;
      
      container.appendChild(shootingStar);
      
      // Remove shooting star after animation
      setTimeout(() => {
        if (shootingStar.parentNode) {
          shootingStar.parentNode.removeChild(shootingStar);
        }
      }, 2000);
    };

    generateStars();
    
    // Regenerate stars on window resize
    const handleResize = () => {
      setTimeout(generateStars, 100);
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div className="star-field" ref={starsRef}>
      {/* Background gradient */}
      <div className="night-sky-gradient"></div>
      
      {/* Nebula effects */}
      <div className="nebula nebula-1"></div>
      <div className="nebula nebula-2"></div>
      <div className="nebula nebula-3"></div>
    </div>
  );
};

export default StarField;