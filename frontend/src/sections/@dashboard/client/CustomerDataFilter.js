import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import PropTypes from 'prop-types';

import { makeStyles } from '@mui/styles';
import {
  Alert,
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
import {
  filterClientsAsync,
  clientsAsync,
  saveCustomerDataFilterAsync,
  saveFilterSuccess,
} from '../../../redux/actions/usersActions';

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
  minRooms: PropTypes.string,
  setMinRooms: PropTypes.func,
  maxRooms: PropTypes.string,
  setMaxRooms: PropTypes.func,
  minBaths: PropTypes.string,
  setMinBaths: PropTypes.func,
  maxBaths: PropTypes.string,
  setMaxBaths: PropTypes.func,
  minSqft: PropTypes.string,
  setMinSqft: PropTypes.func,
  maxSqft: PropTypes.string,
  setMaxSqft: PropTypes.func,
  minLotSqft: PropTypes.string,
  setMinLotSqft: PropTypes.func,
  maxLotSqft: PropTypes.string,
  setMaxLotSqft: PropTypes.func,
  savedFilter: PropTypes.string,
  setSavedFilter: PropTypes.func,
  customerDataFilters: PropTypes.array,
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
  minRooms,
  setMinRooms: handleChangeMinRooms,
  maxRooms,
  setMaxRooms: handleChangeMaxRooms,
  minBaths,
  setMinBaths: handleChangeMinBaths,
  maxBaths,
  setMaxBaths: handleChangeMaxBaths,
  minSqft,
  setMinSqft: handleChangeMinSqft,
  maxSqft,
  setMaxSqft: handleChangeMaxSqft,
  minLotSqft,
  setMinLotSqft: handleChangeMinLotSqft,
  maxLotSqft,
  setMaxLotSqft: handleChangeMaxLotSqft,
  savedFilter,
  setSavedFilter: handleChangeSavedFilter,
  customerDataFilters,
}) {
  const classes = useStyles();
  const [showFilters, setShowFilters] = useState(false);
  const [showClearFilters, setShowClearFilters] = useState(false);
  const [showSaveFilter, setShowSaveFilter] = useState(false);
  const [forZapier, setForZapier] = useState(false);
  const [alertOpen, setAlertOpen] = useState(false);
  const [error, setError] = useState('');
  const [filterName, setFilterName] = useState('');
  const dispatch = useDispatch();

  const filterSuccess = useSelector(saveFilterSuccess);

  const handleChangeTagFilter = (event) => {
    const { value } = event.target;
    handleTagFiltersChange((prevFilters) => {
      if (prevFilters.includes(value)) {
        return prevFilters.filter((filter) => filter !== value);
      }
      return [...prevFilters, value];
    });
  };

  const handleYesChange = () => {
    setForZapier(true);
  };

  const handleNoChange = () => {
    setForZapier(false);
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
      state ||
      minRooms ||
      maxRooms ||
      minBaths ||
      maxBaths ||
      minSqft ||
      maxSqft ||
      minLotSqft ||
      maxLotSqft ||
      savedFilter
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
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
    savedFilter,
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
        customerSinceMax,
        minRooms,
        maxRooms,
        minBaths,
        maxBaths,
        minSqft,
        maxSqft,
        minLotSqft,
        maxLotSqft,
        savedFilter
      )
    );
    setShowFilters(false);
  };

  const handleShowFilters = () => {
    if (product === 'price_1MhxfPAkLES5P4qQbu8O45xy') {
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
    handleChangeMinRooms('');
    handleChangeMaxRooms('');
    handleChangeMinBaths('');
    handleChangeMaxBaths('');
    handleChangeMinSqft('');
    handleChangeMaxSqft('');
    handleChangeMinLotSqft('');
    handleChangeMaxLotSqft('');
    handleChangeSavedFilter('');
    dispatch(clientsAsync(1));
  };

  const handleSavedFilterChange = (event) => {
    // First clear all filters
    handleClearFilters();

    // Then update the saved filter
    handleChangeSavedFilter(event.target.value);
  };

  const handleOpenSaveFilter = () => {
    setShowFilters(false);
    setShowSaveFilter(true);
  };

  const handleSaveFilter = (event) => {
    event.preventDefault();
    if (filterName === '') {
      setError('Please enter a filter name');
      return;
    }
    setError('');
    setAlertOpen(true);
    setShowSaveFilter(false);
    dispatch(
      saveCustomerDataFilterAsync(
        filterName,
        minPrice,
        maxPrice,
        minYear,
        maxYear,
        equipInstallDateMin,
        equipInstallDateMax,
        tagFilters,
        city,
        state,
        zipCode,
        minRooms,
        maxRooms,
        minBaths,
        maxBaths,
        minSqft,
        maxSqft,
        minLotSqft,
        maxLotSqft,
        forZapier
      )
    );
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
                {customerDataFilters && (
                  <Grid item xs={12}>
                    <FormControl component="fieldset">
                      <Typography variant="h6" mb={2}>
                        Saved Filters
                      </Typography>
                      <Grid container spacing={1}>
                        {customerDataFilters.map((option) => (
                          <FormControlLabel
                            key={option}
                            control={
                              <Checkbox
                                checked={savedFilter === option}
                                onChange={handleSavedFilterChange}
                                value={option}
                              />
                            }
                            label={option}
                          />
                        ))}
                      </Grid>
                    </FormControl>
                  </Grid>
                )}
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
                  <Tooltip title="How many bedrooms the house has">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Bedrooms
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <FormControl fullWidth>
                          <InputLabel>Min Bedrooms</InputLabel>
                          <Input
                            type="number"
                            value={minRooms}
                            onChange={(event) => handleChangeMinRooms(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Max Bedrooms</InputLabel>
                          <Input
                            type="number"
                            value={maxRooms}
                            onChange={(event) => handleChangeMaxRooms(event.target.value)}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <Tooltip title="How many bathrooms the house has">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Bathrooms
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <FormControl fullWidth>
                          <InputLabel>Min Bathrooms</InputLabel>
                          <Input
                            type="number"
                            value={minBaths}
                            onChange={(event) => handleChangeMinBaths(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Max Bathrooms</InputLabel>
                          <Input
                            type="number"
                            value={maxBaths}
                            onChange={(event) => handleChangeMaxBaths(event.target.value)}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <Tooltip title="How many square feet the house is">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Square Feet
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <FormControl fullWidth>
                          <InputLabel>Min Square Feet</InputLabel>
                          <Input
                            type="number"
                            value={minSqft}
                            onChange={(event) => handleChangeMinSqft(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Max Square Feet</InputLabel>
                          <Input
                            type="number"
                            value={maxSqft}
                            onChange={(event) => handleChangeMaxSqft(event.target.value)}
                          />
                        </FormControl>
                      </Stack>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <Tooltip title="How large the lot size is for the property. This is based off square feet">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Lot Size
                      </Typography>
                      <Stack direction="row" spacing={2} alignItems="center">
                        <FormControl fullWidth>
                          <InputLabel>Min Lot Size</InputLabel>
                          <Input
                            type="number"
                            value={minLotSqft}
                            onChange={(event) => handleChangeMinLotSqft(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Max Lot Size</InputLabel>
                          <Input
                            type="number"
                            value={maxLotSqft}
                            onChange={(event) => handleChangeMaxLotSqft(event.target.value)}
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
              <Box mt={2} alignItems="center" display="flex" justifyContent="space-between">
                <Button onClick={handleOpenSaveFilter} variant="contained" color="primary">
                  Save Filter
                </Button>
                <Box ml={2}>
                  <Button type="submit" variant="contained" color="primary">
                    Apply Filters
                  </Button>
                </Box>
              </Box>
            </form>
          </DialogContent>
        </Dialog>
      )}
      {showSaveFilter && (
        <Dialog
          sx={{ padding: '200px' }}
          className={classes.filterBox}
          open={showSaveFilter}
          onClose={() => setShowSaveFilter(false)}
        >
          <DialogTitle>Save Filter</DialogTitle>
          <Divider />
          <DialogContent>
            <form onSubmit={handleSaveFilter}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Tooltip title="What Do You Want To Name The Filter">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Filter Name<span style={{ color: 'red' }}> *</span>
                      </Typography>
                      {error && (
                        <Grid item xs={12}>
                          <Typography color="error">{error}</Typography>
                        </Grid>
                      )}
                      <FormControl fullWidth>
                        <InputLabel>Name</InputLabel>
                        <Input
                          type="string"
                          value={filterName}
                          onChange={(event) => setFilterName(event.target.value)}
                        />
                      </FormControl>
                    </Box>
                  </Tooltip>
                </Grid>
                <Grid item xs={12}>
                  <Tooltip title="Do you want new listing instances that match this filter to be sent to Zapier?">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Trigger Zapier Automation
                      </Typography>
                      <FormControlLabel
                        control={<Checkbox checked={forZapier} onChange={handleYesChange} />}
                        label="Yes"
                      />
                      <FormControlLabel
                        control={<Checkbox checked={!forZapier} onChange={handleNoChange} />}
                        label="No"
                      />
                    </Box>
                  </Tooltip>
                </Grid>
              </Grid>
              <Box mt={2} alignItems="center" display="flex" justifyContent="space-between">
                <Button onClick={handleSaveFilter} variant="contained" color="primary">
                  Save Filter
                </Button>
              </Box>
            </form>
          </DialogContent>
        </Dialog>
      )}
      {alertOpen && filterSuccess && (
        <Alert severity="success" onClose={() => setAlertOpen(false)}>
          Filter Saved!
        </Alert>
      )}
    </div>
  );
}
