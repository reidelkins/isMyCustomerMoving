// Page which appears when the site is under maintenance

import React from 'react';
// import { Helmet } from 'react-helmet';
import { Box, Container, Typography } from '@mui/material';

const Maintenance = () => (
    <>
        {/* <Helmet>
            <title>Maintenance | isMyCustomerMoving</title>
        </Helmet> */}
        <Box
            sx={{
                backgroundColor: 'background.default',
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                justifyContent: 'center'
            }}
        >
            <Container maxWidth="md">
                <Box sx={{ textAlign: 'center' }}>
                    <img
                        alt="Under maintenance"
                        src="/static/illustrations/illustration_login.png"
                        style={{
                            height: 'auto',
                            marginBottom: 50,
                            marginTop: 50,
                            marginLeft: 'auto',
                            marginRight: 'auto',
                            width: '80%'
                        }}
                    />
                    <Typography
                        color="textPrimary"
                        variant="h1"
                    >
                        We&apos;ll be back soon
                    </Typography>
                    <Typography
                        color="textSecondary"
                        sx={{ mb: 3 }}
                        variant="subtitle2"
                    >
                        We are currently performing scheduled maintenance.
                        <br />
                        We should be back shortly.
                    </Typography>
                </Box>
            </Container>
        </Box>
    </>
);

export default Maintenance;