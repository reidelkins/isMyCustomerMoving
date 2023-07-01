import PropTypes from 'prop-types';
// material
import { styled } from '@mui/material/styles';
import { Toolbar } from '@mui/material';
// component
import ForSaleDataFilter from './ForSaleDataFilter';
// redux

// ----------------------------------------------------------------------

const RootStyle = styled(Toolbar)(({ theme }) => ({
  height: 96,
  display: 'flex',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1, 0, 3),
}));

ForSaleListToolbar.propTypes = {
  product: PropTypes.string,
  forSaleFilters: PropTypes.array,
  minPrice: PropTypes.string,
  setMinPrice: PropTypes.func,
  maxPrice: PropTypes.string,
  setMaxPrice: PropTypes.func,
  minYear: PropTypes.string,
  setMinYear: PropTypes.func,
  maxYear: PropTypes.string,
  setMaxYear: PropTypes.func,
  minDaysAgo: PropTypes.string,
  setMinDaysAgo: PropTypes.func,
  maxDaysAgo: PropTypes.string,
  setMaxDaysAgo: PropTypes.func,
  savedFilter: PropTypes.string,
  setSavedFilter: PropTypes.func,
  tagFilters: PropTypes.array,
  setTagFilters: PropTypes.func,
  zipCode: PropTypes.string,
  setZipCode: PropTypes.func,
  city: PropTypes.string,
  setCity: PropTypes.func,
  state: PropTypes.string,
  setState: PropTypes.func,
};

// ----------------------------------------------------------------------
export default function ForSaleListToolbar({
  forSaleFilters,
  product,
  minPrice,
  setMinPrice,
  maxPrice,
  setMaxPrice,
  minYear,
  setMinYear,
  maxYear,
  setMaxYear,
  minDaysAgo,
  setMinDaysAgo,
  maxDaysAgo,
  setMaxDaysAgo,
  tagFilters,
  setTagFilters,
  zipCode,
  setZipCode,
  city,
  setCity,
  state,
  setState,
  savedFilter,
  setSavedFilter,
}) {
  return (
    <RootStyle>
      <ForSaleDataFilter
        forSaleFilters={forSaleFilters}
        product={product}
        minPrice={minPrice}
        setMinPrice={setMinPrice}
        maxPrice={maxPrice}
        setMaxPrice={setMaxPrice}
        minYear={minYear}
        setMinYear={setMinYear}
        maxYear={maxYear}
        setMaxYear={setMaxYear}
        minDaysAgo={minDaysAgo}
        setMinDaysAgo={setMinDaysAgo}
        maxDaysAgo={maxDaysAgo}
        setMaxDaysAgo={setMaxDaysAgo}
        tagFilters={tagFilters}
        setTagFilters={setTagFilters}
        zipCode={zipCode}
        setZipCode={setZipCode}
        city={city}
        setCity={setCity}
        state={state}
        setState={setState}
        savedFilter={savedFilter}
        setSavedFilter={setSavedFilter}
      />
    </RootStyle>
  );
}