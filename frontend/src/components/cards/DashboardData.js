import React from 'react';
import Box from '@mui/material/Box';
import { Typography } from '@mui/material';
import PropTypes from 'prop-types';

const DashboardData = ({ mainText, topText, bottomText, color, icon: Icon }) => (
  <Box
    sx={{
      width: '23%', // arbitrary size
      height: '15vh', // 15% of viewport height
      bgcolor: '#ffffff',
      position: 'relative',
      p: 2,
      display: 'flex', // use flexbox
      flexDirection: 'column', // stack items vertically
      justifyContent: 'space-between', // distribute space evenly between items
    }}
  >
    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '1.5vh', mb: 1 }}>
      {topText}
    </Typography>
    <Typography variant="body1" color="text.primary" sx={{ fontSize: '3vh', mb: 1 }}>
      {mainText}
    </Typography>
    <Typography
      variant="body2"
      color="text.secondary"
      sx={{
        fontSize: '1.5vh',
        maxWidth: '50%',
        wordWrap: 'break-word',
      }}
    >
      {bottomText}
    </Typography>

    <Box
      sx={{
        position: 'absolute', // Set position to relative so the image will position absolutely to this box
        right: 0,
        top: 0,
        bottom: 0,
        width: '100%',
        height: '100%',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: "27%", // Width of the circle
          height: '15vh', // Half of the width to get semi-circle
          borderRadius: '50% 0 0 50%', // To get semi-circle shape
          bgcolor: color, // Color of the semi-circle
          opacity: 0.5,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          right: 0,
          top: 0,
          bottom: 0,
          width: "27%", // Width of the circle
          height: '15vh', // Half of the width to get semi-circle
          borderRadius: '50% 0 0 50%', // To get semi-circle shape
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <img src={Icon} alt="Logo" style={{ width: '50%' }} />
      </Box>
    </Box>
  </Box>
);

DashboardData.propTypes = {
  mainText: PropTypes.number.isRequired,
  topText: PropTypes.string.isRequired,
  bottomText: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
};

export default DashboardData;
