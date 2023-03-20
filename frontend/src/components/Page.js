import PropTypes from 'prop-types';
import { Helmet } from 'react-helmet-async';
import { forwardRef } from 'react';
// @mui
import { Box, Alert } from '@mui/material';

// ----------------------------------------------------------------------

const Page = forwardRef(({ children, userInfo = null, title = '', meta, ...other }, ref) => (
  <>
    <Helmet>
      <title>{`${title} | Did My Customer Move`}</title>
      {meta}
    </Helmet>

    <Box ref={ref} {...other}>
      {userInfo && userInfo.company.product === "price_1Mi1KuAkLES5P4qQ2MEEwV9l" && (        
          <Alert            
            sx={{ mb: 2, mx: 'auto', width: '100%' }}
            variant="filled"
            severity="info"
          >
            You do not get access to which customers are moving or have recently moved or any of our other premium features because you are signed up for the free tier. <br/><strong>Click the Upgrade button on the home page to never lose a customer again!</strong>
          </Alert>
        )}
      {children}
    </Box>
  </>
));

Page.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  meta: PropTypes.node,
};

export default Page;
