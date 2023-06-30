import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import PropTypes from 'prop-types';

import { makeStyles } from '@mui/styles';
import {
  Box,
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormLabel,
  Grid,
  Input,
  InputLabel,
  Typography,
  Tooltip,
  IconButton,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  Stack,
} from '@mui/material';

import Iconify from '../../../components/Iconify';
import { filterClientsAsync, clientsAsync } from '../../../redux/actions/usersActions';

const useStyles = makeStyles((theme) => ({
  root: {
    position: 'relative',
  },
  filterButton: {
    position: 'absolute',
    right: theme.spacing(1),
    top: theme.spacing(1),
  },
  filterBox: {
    position: 'absolute',
    margin: 'auto',
    maxHeight: '50vh',
    overflowY: 'auto',
    backgroundColor: theme.palette.background.paper,
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2),
    width: '30%',
    minWidth: '500px',
  },
}));

CustomerDataFilter.propTypes = {
  product: PropTypes.string.isRequired,
  minPrice: PropTypes.string,
  setMinPrice: PropTypes.func,
  maxPrice: PropTypes.string,
  setMaxPrice: PropTypes.func,
  minYear: PropTypes.string,
  setMinYear: PropTypes.func,
  maxYear: PropTypes.string,
  setMaxYear: PropTypes.func,
  equipInstallDateMin: PropTypes.string,
  setEquipInstallDateMin: PropTypes.func,
  equipInstallDateMax: PropTypes.string,
  setEquipInstallDateMax: PropTypes.func,
  statusFilters: PropTypes.array,
  setStatusFilters: PropTypes.func,
  tagFilters: PropTypes.array,
  setTagFilters: PropTypes.func,
  zipCode: PropTypes.string,
  setZipCode: PropTypes.func,
  city: PropTypes.string,
  setCity: PropTypes.func,
  state: PropTypes.string,
  setState: PropTypes.func,
  customerSinceMin: PropTypes.string,
  setCustomerSinceMin: PropTypes.func,
  customerSinceMax: PropTypes.string,
  setCustomerSinceMax: PropTypes.func,
};

export default function CustomerDataFilter({
  product,
  minPrice,
  setMinPrice: handleChangeMinPrice,
  maxPrice,
  setMaxPrice: handleChangeMaxPrice,
  minYear,
  setMinYear: handleChangeMinYear,
  maxYear,
  setMaxYear: handleChangeMaxYear,
  equipInstallDateMin,
  setEquipInstallDateMin: handleEquipInstallDateMin,
  equipInstallDateMax,
  setEquipInstallDateMax: handleEquipInstallDateMax,
  statusFilters,
  setStatusFilters: handleStatusFiltersChange,
  tagFilters,
  setTagFilters: handleTagFiltersChange,
  zipCode,
  setZipCode: handleZipCodeChange,
  city,
  setCity: handleCityChange,
  state,
  setState: handleStateChange,
  customerSinceMin,
  setCustomerSinceMin: handleCustomerSinceMin,
  customerSinceMax,
  setCustomerSinceMax: handleCustomerSinceMax,
}) {
  const classes = useStyles();
  const [showFilters, setShowFilters] = useState(false);
  const [showClearFilters, setShowClearFilters] = useState(false);
  const dispatch = useDispatch();

  const handleChangeTagFilter = (event) => {
    const { value } = event.target;
    handleTagFiltersChange((prevFilters) => {
      if (prevFilters.includes(value)) {
        return prevFilters.filter((filter) => filter !== value);
      }
      return [...prevFilters, value];
    });
  };

  useEffect(() => {
    if (
      minPrice ||
      maxPrice ||
      minYear ||
      maxYear ||
      equipInstallDateMin ||
      equipInstallDateMax ||
      tagFilters.length > 0 ||
      statusFilters.length > 0 ||
      zipCode ||
      city ||
      state
    ) {
      setShowClearFilters(true);
    } else {
      setShowClearFilters(false);
    }
  }, [
    minPrice,
    maxPrice,
    minYear,
    maxYear,
    equipInstallDateMin,
    equipInstallDateMax,
    tagFilters,
    statusFilters,
    zipCode,
    city,
    state,
  ]);

  const tagOptions = [
    { value: 'garage_3_or_more', label: 'Garage 3+' },
    { value: 'well_water', label: 'Well Water' },
    { value: 'garage_1_or_more', label: 'Garage 1+' },
    { value: 'central_heat', label: 'Central Heat' },
    { value: 'central_air', label: 'Central Air' },
    { value: 'forced_air', label: 'Forced Air' },
    { value: 'solar_panels', label: 'Solar Panels' },
    { value: 'solar_system', label: 'Solar System' },
    { value: 'swimming_pool', label: 'Swimming Pool' },
    { value: 'new roof', label: 'New Roof' },
    { value: 'new_construction', label: 'New Construction' },
    { value: 'fixer_upper', label: 'Fixer Upper' },
    { value: 'fireplace', label: 'Fireplace' },
    { value: 'energy_efficient', label: 'Energy Efficient' },
    { value: 'ocean_view', label: 'Ocean View' },
    { value: 'efficient', label: 'Efficient' },
    { value: 'smart_homes', label: 'Smart Homes' },
    { value: 'guest_house', label: 'Guest House' },
    { value: 'rental_property', label: 'Rental Property' },
    { value: 'no_hoa', label: 'No HOA' },
    { value: 'hoa', label: 'HOA' },
    { value: 'beach', label: 'Beach' },
  ];

  const sortedTagOptions = tagOptions.sort((a, b) => {
    const labelA = a.label.toUpperCase();
    const labelB = b.label.toUpperCase();
    if (labelA < labelB) {
      return -1;
    }
    if (labelA > labelB) {
      return 1;
    }
    return 0;
  });

  const handleStatusFilterChange = (event) => {
    const { value } = event.target;
    handleStatusFiltersChange((prevFilters) => {
      if (prevFilters.includes(value)) {
        return prevFilters.filter((filter) => filter !== value);
      }
      return [...prevFilters, value];
    });
  };

  const statusOptions = [
    { value: 'For Sale', label: 'For Sale' },
    { value: 'Recently Sold', label: 'Recently Sold' },
    { value: 'Off Market', label: 'Off Market' },
  ];

  const handleFilterSubmit = (event) => {
    event.preventDefault();
    // Filter data based on selected filters
    dispatch(
      filterClientsAsync(
        statusFilters,
        minPrice,
        maxPrice,
        minYear,
        maxYear,
        tagFilters,
        equipInstallDateMin,
        equipInstallDateMax,
        city,
        state,
        zipCode,
        customerSinceMin,
        customerSinceMax
      )
    );
    setShowFilters(false);
  };

  const handleShowFilters = () => {
    if (product.product === 'price_1MhxfPAkLES5P4qQbu8O45xy') {
      // eslint-disable-next-line no-alert
      alert('Please upgrade your plan to access this feature');
    } else {
      setShowFilters(true);
    }
  };

  const handleClearFilters = () => {
    handleStatusFiltersChange([]);
    handleChangeMinPrice('');
    handleChangeMaxPrice('');
    handleChangeMinYear('');
    handleChangeMaxYear('');
    handleTagFiltersChange([]);
    handleCityChange('');
    handleStateChange('');
    handleZipCodeChange('');
    handleEquipInstallDateMax('');
    handleEquipInstallDateMin('');
    handleCustomerSinceMin('');
    handleCustomerSinceMax('');
    dispatch(clientsAsync(1));
  };

  return (
    <div className={classes.root}>
      <Stack direction="row" spacing={2} alignItems="space-between">
        <Tooltip title="Filter list">
          <IconButton onClick={handleShowFilters}>
            <Iconify icon="ic:round-filter-list" />
          </IconButton>
        </Tooltip>
        {showClearFilters && (
          <Tooltip title="Clear filters">
            <IconButton onClick={handleClearFilters}>
              <Iconify icon="ic:baseline-clear" />
            </IconButton>
          </Tooltip>
        )}
      </Stack>
      {showFilters && (
        <Dialog
          sx={{ padding: '200px' }}
          className={classes.filterBox}
          open={showFilters}
          onClose={() => setShowFilters(false)}
        >
          <DialogTitle>Filter List</DialogTitle>
          <Divider />
          <DialogContent>
            <form onSubmit={handleFilterSubmit}>
              <Box mb={2}>
                <Typography variant="h6">Select Filters</Typography>
                <Typography variant="body2">
                  Note: Most filters are only relevant for clients where status is not "No Change"
                </Typography>
              </Box>
              <Grid container spacing={2}>
                <Tooltip title="Client Status">
                  <Grid item xs={12}>
                    {statusOptions.map((option) => (
                      <FormControlLabel
                        key={option.value}
                        control={
                          <Checkbox
                            checked={statusFilters.includes(option.value)}
                            onChange={handleStatusFilterChange}
                            value={option.value}
                          />
                        }
                        label={option.label}
                      />
                    ))}
                  </Grid>
                </Tooltip>
                <Grid item xs={12}>
                  <Tooltip title="This will filter for the city state and zip of the home">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Location
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <FormControl fullWidth>
                          <InputLabel>Zip Code</InputLabel>
                          <Input
                            type="number"
                            value={zipCode}
                            onChange={(event) => handleZipCodeChange(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>City</InputLabel>
                          <Input type="text" value={city} onChange={(event) => handleCityChange(event.target.value)} />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>State</InputLabel>
                          <Input
                            type="text"
                            value={state}
                            onChange={(event) => handleStateChange(event.target.value)}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <Tooltip title="This will filter for the price that the house was either sold or listed for">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Housing Price
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="space-between">
                        <FormControl fullWidth>
                          <InputLabel>Min Price</InputLabel>
                          <Input
                            type="number"
                            value={minPrice}
                            onChange={(event) => handleChangeMinPrice(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Max Price</InputLabel>
                          <Input
                            type="number"
                            value={maxPrice}
                            onChange={(event) => handleChangeMaxPrice(event.target.value)}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <Tooltip title="How long have they been one of your customers">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Customer Since
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="space-between">
                        <FormControl fullWidth>
                          <InputLabel>Min Year</InputLabel>
                          <Input
                            type="number"
                            value={customerSinceMin}
                            onChange={(event) => handleCustomerSinceMin(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Max Year</InputLabel>
                          <Input
                            type="number"
                            value={customerSinceMax}
                            onChange={(event) => handleCustomerSinceMax(event.target.value)}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <Tooltip title="Time range that the equipment was installed at the location for the client">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Equipment Installation Date
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="space-between">
                        <FormControl fullWidth>
                          <Input
                            type="date"
                            value={equipInstallDateMin}
                            onChange={(event) => handleEquipInstallDateMin(event.target.value)}
                            startAdornment={<InputLabel shrink>Earliest</InputLabel>}
                          />
                        </FormControl>

                        <FormControl fullWidth>
                          <Input
                            type="date"
                            value={equipInstallDateMax}
                            onChange={(event) => handleEquipInstallDateMax(event.target.value)}
                            startAdornment={<InputLabel shrink>Latest</InputLabel>}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>

                <Grid item xs={12}>
                  <Tooltip title="Year the house was built">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Year Built
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="space-between">
                        <FormControl fullWidth>
                          <InputLabel>Min Year Built</InputLabel>
                          <Input
                            type="number"
                            value={minYear}
                            onChange={(event) => handleChangeMinYear(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Max Year Built</InputLabel>
                          <Input
                            type="number"
                            value={maxYear}
                            onChange={(event) => handleChangeMaxYear(event.target.value)}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <FormLabel component="legend">Tags</FormLabel>
                    <Grid container spacing={1}>
                      {sortedTagOptions.map((option) => (
                        <FormControlLabel
                          key={option.value}
                          control={
                            <Checkbox
                              checked={tagFilters.includes(option.value)}
                              onChange={handleChangeTagFilter}
                              value={option.value}
                            />
                          }
                          label={option.label}
                        />
                      ))}
                    </Grid>
                  </FormControl>
                </Grid>
              </Grid>
              <Box mt={2}>
                <Button type="submit" variant="contained" color="primary">
                  Apply Filters
                </Button>
              </Box>
            </form>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
