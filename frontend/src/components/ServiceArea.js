import React from "react"
import PropTypes from 'prop-types';

import { Box, Typography } from '@mui/material';

import FileUploader from "./FileUploader";
import Map from "./Map";

ServiceArea.propTypes = {
  serviceAreas: PropTypes.array.isRequired,  
};

function ServiceArea({serviceAreas}) {
    return (
        <Box>
            <Typography variant="h3" sx={{ mt: 5 }}>
            Service Area
            </Typography>
            <Map mapClass={"map-container"} mapCardStyle={"service-area-map-card-style"} mapCenter={{ lat: 39.5, lng: -98.35 }} zoomLevel={6.5} serviceAreas={serviceAreas}/>
            <Box sx={{ mt: 5, width: "30%" }}>
                <FileUploader fileType={"ServiceArea"}/>
            </Box>

        </Box>
    )
}

export default ServiceArea;
