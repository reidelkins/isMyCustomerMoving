import React, { useState } from 'react';
import {  
  IconButton,
  Modal,
  Fade,
  Box,
  Typography,
} from '@mui/material';

import Iconify from './Iconify';

const ServiceTitanHelpModal = () => {
    const [integrateInfo, setIntegrateInfo] = useState(false);
    return (
        <>
            <IconButton onClick={() => setIntegrateInfo(true)}>
                <Iconify icon="bi:question-circle-fill" />
            </IconButton>      
            <Modal
            open={integrateInfo}
            onClose={() => setIntegrateInfo(false)}
            closeAfterTransition
            aria-labelledby="modal-modal-title"
            aria-describedby="modal-modal-description"
            padding="10"
            >
            <Fade in={integrateInfo}>
                <Box
                sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: 400,
                    bgcolor: 'white',
                    border: '2px solid #000',
                    boxShadow: '24px',
                    p: '4%',
                }}
                >
                <Typography id="modal-modal-title" variant="h5" component="h2">
                    Add Service Titan Tag IDs Instructions
                </Typography>
                <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                    1. Adding Tag IDs will enable automatically updating your customer list on service titan with the
                    information found from IMCM <br />
                    <br />
                    2. First to make a new tag, log in to service titan, go to settings, search for tag, and click tag types,
                    then click add. <br />
                    <br />
                    3. Next choose a color, a name (like "For Sale or Home Listed"), then click save. <br />
                    <br />
                    4. You then need to scroll the list of tags to find the one you just made. Once found, click the edit
                    button on the row of that tag. <br />
                    <br />
                    5. Copy the ID number from the URL. It will be a long number like 1234567890. <br />
                    <br />
                    <br />
                    Note: You can make 2 different tags for this data or you can make one tag and use the same ID for all 2.
                    <br />
                    The last two tags are so you can keep track on Service Titan once you have marked a client as contacted
                    within our system and differentiate your marketing campaigns with this data. Click{' '}
                    <a href="https://www.loom.com/share/523b171ab81e47f2a050e1b28704c30e" target="_blank" rel="noreferrer">
                    here{' '}
                    </a>{' '}
                    to see a video walking through this process.
                </Typography>
                </Box>
            </Fade>
            </Modal>
        </>
    )
}

export default ServiceTitanHelpModal;