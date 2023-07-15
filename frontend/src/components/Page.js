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
      <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      <link rel="manifest" href="/site.webmanifest" />
      <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#5bbad5" />
      <meta name="msapplication-TileColor" content="#da532c" />
      <meta name="theme-color" content="#ffffff" />
      {meta}
    </Helmet>

    <Box ref={ref} {...other}>
      {userInfo && userInfo.company.product.id === 'price_1MhxfPAkLES5P4qQbu8O45xy' && (
        <Alert sx={{ mb: 2, mx: 'auto', width: '100%' }} variant="filled" severity="info">
          You do not get access to which customers are moving or have recently moved or any of our other premium
          features because you are signed up for the free tier. <br />
          <strong>
            <em>Click the Upgrade button on the home page to never lose a customer again!</em>
          </strong>
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
  userInfo: PropTypes.object,
};

export default Page;
