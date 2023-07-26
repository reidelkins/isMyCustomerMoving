/*
=========================================================
* Material Kit 2 React - v2.0.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-kit-react
* Copyright 2021 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// prop-types is a library for typechecking of props.
import PropTypes from 'prop-types';

// react-countup component
import CountUp from 'react-countup';

// Material Kit 2 React components
import { Box, Typography } from '@mui/material';

CounterCard.propTypes = {
  color: PropTypes.oneOf(['primary', 'secondary', 'info', 'success', 'warning', 'error', 'light', 'dark']),
  start: PropTypes.number.isRequired,
  end: PropTypes.number.isRequired,
  title: PropTypes.string,
  description: PropTypes.string,
};

function CounterCard({ color, start, end, title, description, ...rest }) {
  return (
    <Box p={2} textAlign="center" lineHeight={1}>
      <Typography variant="h2" color={color}>
        <CountUp start={start} end={end} duration={1} {...rest} />
      </Typography>
      {title && (
        <Typography variant="h3" mt={2} mb={1}>
          {title}
        </Typography>
      )}
      {description && (
        <Typography variant="body2" color="text">
          {description}
        </Typography>
      )}
    </Box>
  );
}

// Setting default props for the DefaultCounterCard
// CounterCard.defaultProps = {
//   color: "info",
//   description: "",
//   title: "",
// };

// Typechecking props for the DefaultCounterCard
// CounterCard.propTypes = {
//   color: PropTypes.oneOf([
//     "primary",
//     "secondary",
//     "info",
//     "success",
//     "warning",
//     "error",
//     "light",
//     "dark",
//   ]),
//   count: PropTypes.number.isRequired,
//   title: PropTypes.string,
//   description: PropTypes.string,
// };

export default CounterCard;
