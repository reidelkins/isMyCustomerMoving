import PropTypes from 'prop-types';
// material
import { styled } from '@mui/material/styles';
import { Toolbar } from '@mui/material';
// component
import RecentlySoldDataFilter from './RecentlySoldDataFilter';
// redux

// ----------------------------------------------------------------------

const RootStyle = styled(Toolbar)(({ theme }) => ({
  height: 96,
  display: 'flex',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1, 0, 3),
}));

RecentlySoldListToolbar.propTypes = {
  product: PropTypes.string,
  minPrice: PropTypes.string,
  setMinPrice: PropTypes.func,
  maxPrice: PropTypes.string,
  setMaxPrice: PropTypes.func,
  minYear: PropTypes.string,
  setMinYear: PropTypes.func,
  maxYear: PropTypes.string,
  setMaxYear: PropTypes.func,

};

// ----------------------------------------------------------------------
export default function RecentlySoldListToolbar(product, minPrice, setMinPrice, maxPrice, setMaxPrice, minYear, setMinYear, maxYear, setMaxYear,) {

  return (
    <RootStyle>      
        <RecentlySoldDataFilter 
          product={product}
          minPrice={minPrice}
          setMinPrice={setMinPrice}
          maxPrice={maxPrice}
          setMaxPrice={setMaxPrice}
          minYear={minYear}
          setMinYear={setMinYear}
          maxYear={maxYear}
          setMaxYear={setMaxYear}
        />
    </RootStyle>
  );
}
