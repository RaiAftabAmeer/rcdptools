import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUploadModal.css';

const FileUploadModal = ({ onUpload, onClose, loading }) => {
  const [files, setFiles] = useState({
    currentMonth: null,
    lastMonth: null
  });
  const [dates, setDates] = useState({
    yesterday: '',
    today: ''
  });

  // Set default dates
  React.useEffect(() => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const formatDate = (date) => {
      const day = date.getDate().toString().padStart(2, '0');
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const month = monthNames[date.getMonth()];
      const year = date.getFullYear().toString().slice(-2);
      return `${day}-${month}-${year}`;
    };

    setDates({
      yesterday: formatDate(yesterday),
      today: formatDate(today)
    });
  }, []);

  const createDropzone = (fileType) => {
    return useDropzone({
      accept: {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        'application/vnd.ms-excel': ['.xls']
      },
      multiple: false,
      onDrop: (acceptedFiles) => {
        if (acceptedFiles.length > 0) {
          setFiles(prev => ({
            ...prev,
            [fileType]: acceptedFiles[0]
          }));
        }
      }
    });
  };

  const currentMonthDropzone = createDropzone('currentMonth');
  const lastMonthDropzone = createDropzone('lastMonth');

  const handleSubmit = () => {
    onUpload(files, dates);
  };

  const handleDateChange = (dateType, value) => {
    // Convert standard date input to dd-mmm-yy format
    if (value) {
      const date = new Date(value);
      const day = date.getDate().toString().padStart(2, '0');
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const month = monthNames[date.getMonth()];
      const year = date.getFullYear().toString().slice(-2);
      const formattedDate = `${day}-${month}-${year}`;
      
      setDates(prev => ({
        ...prev,
        [dateType]: formattedDate
      }));
    }
  };

  const canSubmit = files.currentMonth && files.lastMonth && !loading;

  return (
    <div className="modal-overlay">
      <div className="upload-modal">
        <div className="modal-header">
          <h2>Upload Excel Files</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          {/* Instructions */}
          <div className="instructions">
            <h3>Instructions</h3>
            <ol>
              <li>Select both Current Month and Last Month Excel files</li>
              <li>Set the date filters for yesterday and today</li>
              <li>Click "Process Files" to analyze the data</li>
              <li>View the results in the 3D dashboard below</li>
            </ol>
          </div>

          {/* File Upload Areas */}
          <div className="upload-areas">
            <div className="upload-section">
              <h4>Current Month Data</h4>
              <div 
                {...currentMonthDropzone.getRootProps()} 
                className={`dropzone ${currentMonthDropzone.isDragActive ? 'active' : ''} ${files.currentMonth ? 'has-file' : ''}`}
              >
                <input {...currentMonthDropzone.getInputProps()} />
                <div className="dropzone-content">
                  {files.currentMonth ? (
                    <>
                      <span className="file-icon">📊</span>
                      <p className="file-name">{files.currentMonth.name}</p>
                      <p className="file-size">{(files.currentMonth.size / 1024).toFixed(1)} KB</p>
                    </>
                  ) : (
                    <>
                      <span className="upload-icon">📁</span>
                      <p>Drag & drop Excel file here</p>
                      <p className="upload-hint">or click to browse</p>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="upload-section">
              <h4>Last Month Data</h4>
              <div 
                {...lastMonthDropzone.getRootProps()} 
                className={`dropzone ${lastMonthDropzone.isDragActive ? 'active' : ''} ${files.lastMonth ? 'has-file' : ''}`}
              >
                <input {...lastMonthDropzone.getInputProps()} />
                <div className="dropzone-content">
                  {files.lastMonth ? (
                    <>
                      <span className="file-icon">📊</span>
                      <p className="file-name">{files.lastMonth.name}</p>
                      <p className="file-size">{(files.lastMonth.size / 1024).toFixed(1)} KB</p>
                    </>
                  ) : (
                    <>
                      <span className="upload-icon">📁</span>
                      <p>Drag & drop Excel file here</p>
                      <p className="upload-hint">or click to browse</p>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Date Filters */}
          <div className="date-filters">
            <h4>Date Filters</h4>
            <div className="date-inputs">
              <div className="date-input-group">
                <label>Yesterday Date:</label>
                <input 
                  type="date" 
                  onChange={(e) => handleDateChange('yesterday', e.target.value)}
                  defaultValue={new Date(Date.now() - 86400000).toISOString().split('T')[0]}
                />
                <span className="formatted-date">{dates.yesterday}</span>
              </div>
              <div className="date-input-group">
                <label>Today Date:</label>
                <input 
                  type="date" 
                  onChange={(e) => handleDateChange('today', e.target.value)}
                  defaultValue={new Date().toISOString().split('T')[0]}
                />
                <span className="formatted-date">{dates.today}</span>
              </div>
            </div>
          </div>

          {/* Column Mapping Info */}
          <div className="column-mapping">
            <h4>Expected Excel Format</h4>
            <p>Your Excel files should contain the following columns in order:</p>
            <div className="mapping-grid">
              <div>Column B: Member ID</div>
              <div>Column C: Name</div>
              <div>Column E: Branch</div>
              <div>Column F: CO</div>
              <div>Column K: Due Total</div>
              <div>Column O: Current Rec Total</div>
              <div>Column V: Total Overdue</div>
              <div>Column S: Current Advance</div>
              <div>Column R: Opening Advance</div>
              <div>Column X: Disb Date</div>
              <div>Column AA: Last Install Date</div>
              <div>Column AB: OLP</div>
              <div>Column AF: Cell No</div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button 
            className="submit-btn" 
            onClick={handleSubmit} 
            disabled={!canSubmit}
          >
            {loading ? (
              <>
                <div className="loading-spinner"></div>
                Processing...
              </>
            ) : (
              'Process Files'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FileUploadModal;