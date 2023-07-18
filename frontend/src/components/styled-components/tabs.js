import React from 'react';
import PropTypes from 'prop-types';
import { Typography } from '@mui/material';

TabComponent.propTypes = {
    selectedTab: PropTypes.number.isRequired,
    setSelectedTab: PropTypes.func.isRequired,
    tabLabels: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default function TabComponent({selectedTab, setSelectedTab: handleSelectedTabChange, tabLabels}) {  

  const handleTabClick = (index) => {
    handleSelectedTabChange(index);
  };

  const handleTabKeyDown = (event, index) => {
    if (event.key === 'Enter' || event.key === ' ') {
      handleSelectedTabChange(index);
    }
  };

  return (
    <div className="tab-container" style={{
        display: 'flex',
        flexDirection: 'row',
        justifyContent: "flex-start"
    }}>
      <div className="tabs" style={{
        display: 'flex',
        flexDirection: 'row',
        justifyContent: "flex-start",
        width: '100%',    
        marginLeft: '10px',    
    }}>
        {tabLabels.map((label, index) => (
            <div
                key={label}
                className={`tab ${selectedTab === index ? 'selected' : ''}`}
                onClick={() => handleTabClick(index)}
                onKeyDown={(event) => handleTabKeyDown(event, index)}
                tabIndex={index}
                role="button"
                style={{
                    backgroundColor: selectedTab === index ? '#fff' : '#C0C0C0',                    
                    fontWeight: selectedTab === index ? 'bold' : 'normal',
                    // color: selectedTab === index ? '#000' : '#000',
                    marginRight: '2px',
                    marginBottom: '-10px',
                    borderRadius: '10px 10px 0 0',
                    border: '1px solid #000',
                    borderBottom: "none",
                    padding: '5px 10px',
                    height: '50px',
                }}
            >
                <Typography variant="h6" style={{
                    fontSize: '1.2rem',
                    fontWeight: 'bold',
                    color: selectedTab === index ? '#000' : '#000',
                }}>
                    {label}
                </Typography>
            </div>
        ))}        
      </div>      
    </div>
  );
};