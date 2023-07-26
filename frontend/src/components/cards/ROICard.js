import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import { Typography, Divider } from '@mui/material';
import PropTypes from 'prop-types';

const ROICard = ({total, revenues, height, company, monthsActive}) => {
    // const [revenueByMonth, setRevenueByMonth] = React.useState(revenues);
    const price = (company.product.interval === 'month' ? company.product.amount : company.product.amount / 12);
    const [totalROI, setTotalROI] = useState(0);
    const revenuesByMonth = Object.values(revenues);
    const months = Object.keys(revenues);
    const [rois, setROIs] = useState([]);

    useEffect(() => {
        setTotalROI(Math.floor(total / (price * monthsActive)));
        setROIs(revenuesByMonth.map((revenue) => Math.floor(revenue / price)));        
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [total, price]);
    


    return(
    <div style={{ height, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Box
            sx={{
            width: '80%', // arbitrary size
            height: '80%', // 15% of viewport height
            bgcolor: '#ffffff',
            position: 'relative',
            p: 2,
            display: 'flex', // use flexbox
            flexDirection: 'column', // stack items vertically
            border: 2,
            borderColor: 'primary.main',
            marginTop: '10%'
            
            
            }}
        >    
            <Typography variant="body1" color="text.primary" sx={{ fontSize: '3vh', mb: 1, ml: 3 }}>
            Total ROI
            </Typography>
            <Typography variant="body1" color="text.primary" sx={{ fontSize: '6vh', mb: 1, ml: 5 }}>
            {totalROI}x
            </Typography>                                                        
            {months.slice(0, 3).map((month, index) => (
            <div key={month}>
                <Divider />
                <Box key={index} sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', ml: 3, mr: 3 }}>
                    <Typography variant="body1" color="text.primary" sx={{ fontSize: '2vh', mb: 1 }}>
                    {month}
                    </Typography>
                    <Typography variant="body1" color="text.primary" sx={{ fontSize: '2vh', mb: 1 }}>
                    {rois[index]}x
                    </Typography>
                </Box>
            </div>
            ))}                        
        </Box>
    </div>
    );
};

ROICard.propTypes = {
  total: PropTypes.number.isRequired,
  revenues: PropTypes.objectOf(PropTypes.number).isRequired,
  height: PropTypes.string.isRequired,
  company: PropTypes.object,
  monthsActive: PropTypes.number.isRequired
};

export default ROICard;
