import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import { Typography, Divider } from '@mui/material';
import PropTypes from 'prop-types';

const PrevThreeMonths = ({title, total, values, height, company, monthsActive}) => {
    const price = (company.product.interval === 'month' ? company.product.amount : company.product.amount / 12);
    const [totalROI, setTotalROI] = useState(0);
    const [costPerClient, setCostPerClient] = useState(0);
    const valuesByMonth = Object.values(values);
    const months = Object.keys(values);
    const [vals, setVals] = useState([]);

    useEffect(() => {
        if (title === 'Total ROI') {
            setTotalROI(Math.ceil(total / (price * monthsActive)));
        } else {
            setCostPerClient(((price * monthsActive) / total).toFixed(2));
        }
        setVals(valuesByMonth.map((value) => Math.ceil(value / price)));        
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [total, price, title]);

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
                {title}
            </Typography>
            <Typography variant="body1" color="text.primary" sx={{ fontSize: '6vh', mb: 1, ml: 5 }}>
            {title === 'Total ROI' ? `${totalROI}x` : `$${costPerClient}`}
            </Typography>                                                        
            {months.slice(0, 3).map((month, index) => (
            <div key={month}>
                <Divider />
                <Box key={index} sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', ml: 3, mr: 3 }}>
                    <Typography variant="body1" color="text.primary" sx={{ fontSize: '2vh', mb: 1 }}>
                    {month}
                    </Typography>
                    <Typography variant="body1" color="text.primary" sx={{ fontSize: '2vh', mb: 1 }}>
                    {vals[index]}{title === 'Total ROI' && 'x'}
                    </Typography>
                </Box>
            </div>
            ))}                        
        </Box>
    </div>
    );
};

PrevThreeMonths.propTypes = {
  title: PropTypes.string.isRequired,
  total: PropTypes.number.isRequired,
  values: PropTypes.objectOf(PropTypes.number).isRequired,
  height: PropTypes.string.isRequired,
  company: PropTypes.object.isRequired,
  monthsActive: PropTypes.number.isRequired
};

export default PrevThreeMonths;
