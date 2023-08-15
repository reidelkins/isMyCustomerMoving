import React from "react"
import PropTypes from 'prop-types';

import { Box, Typography } from '@mui/material';

import FileUploader from "./FileUploader";

ServiceArea.propTypes = {
  serviceAreas: PropTypes.array.isRequired,  
};

function ServiceArea({serviceAreas}) {
    return (
        <Box>
            <Typography variant="h3" sx={{ mt: 5 }}>
            Service Area
            </Typography>
            {serviceAreas.map((zipCode) => (
                <p key={zipCode} style={{ marginBottom: 20 }}>{zipCode}</p>   
            ))}
            <Box sx={{ mt: 5, width: "30%" }}>
                <FileUploader fileType={"ServiceArea"}/>
            </Box>

        </Box>
    )
}

export default ServiceArea;
