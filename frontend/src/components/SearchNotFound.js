import PropTypes from 'prop-types';
// material
import { Paper, Typography } from '@mui/material';

// ----------------------------------------------------------------------

SearchNotFound.propTypes = {
  searchQuery: PropTypes.string,
  tipe: PropTypes.string
};

export default function SearchNotFound({ tipe, searchQuery = '', ...other }) {
  return (
    <Paper {...other}>
      <Typography gutterBottom align="center" variant="subtitle1">
        Not found
      </Typography>
      {tipe === 'client' ? (
        <Typography variant="body2" align="center">
          No results found for &nbsp;
          <strong>&quot;{searchQuery}&quot;</strong>. Try checking for typos or using complete words.
        </Typography>
      ):(
        <Typography variant="body2" align="center">
          No events available
        </Typography>
      )}
        
    </Paper>
  );
}
