import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

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
  MenuItem,
  Select,
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
  filterRecentlySoldAsync,
  recentlySoldAsync,
  saveFilterAsync,
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

export default function RecentlySoldDataFilter({
  minPrice,
  setMinPrice: handleChangeMinPrice,
  maxPrice,
  setMaxPrice: handleChangeMaxPrice,
  minYear,
  setMinYear: handleChangeMinYear,
  maxYear,
  setMaxYear: handleChangeMaxYear,
  minDaysAgo,
  setMinDaysAgo: handleChangeMinDaysAgo,
  maxDaysAgo,
  setMaxDaysAgo: handleChangeMaxDaysAgo,
  tagFilters,
  setTagFilters: handleChangeTagFilters,
  zipCode,
  setZipCode: handleChangeZipCode,
  city,
  setCity: handleChangeCity,
  state,
  setState: handleChangeState,
  savedFilter,
  setSavedFilter: handleChangeSavedFilter,
  recentlySoldFilters,
}) {
  const classes = useStyles();
  const [showFilters, setShowFilters] = useState(false);
  const [showSaveFilter, setShowSaveFilter] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [showClearFilters, setShowClearFilters] = useState(false);
  const [error, setError] = useState('');
  const [forZapier, setForZapier] = useState(false);
  const [alertOpen, setAlertOpen] = useState(false);
  const dispatch = useDispatch();

  const filterSuccess = useSelector(saveFilterSuccess);

  const handleYesChange = () => {
    setForZapier(true);
  };

  const handleNoChange = () => {
    setForZapier(false);
  };

  const handleTagFilterChange = (event) => {
    const { value } = event.target;
    handleChangeTagFilters((prevFilters) => {
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
      minDaysAgo !== 0 ||
      maxDaysAgo !== 30 ||
      tagFilters.length > 0 ||
      zipCode ||
      city ||
      state ||
      savedFilter
    ) {
      setShowClearFilters(true);
    } else {
      setShowClearFilters(false);
    }
  }, [minPrice, maxPrice, minYear, maxYear, minDaysAgo, maxDaysAgo, tagFilters, zipCode, city, state, savedFilter]);

  const handleClearFilters = () => {
    handleChangeMinPrice('');
    handleChangeMaxPrice('');
    handleChangeMinYear('');
    handleChangeMaxYear('');
    handleChangeMinDaysAgo('0');
    handleChangeMaxDaysAgo('30');
    handleChangeTagFilters([]);
    handleChangeZipCode('');
    handleChangeCity('');
    handleChangeState('');
  };

  const handleClearFilterButtonPressed = () => {
    handleClearFilters();
    handleChangeSavedFilter('');
    setError('');
    dispatch(recentlySoldAsync(1));
  };

  const handleSavedFilterChange = (event) => {
    // First clear all filters
    handleClearFilters();

    // Then update the saved filter
    handleChangeSavedFilter(event.target.value);
  };

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

  const handleDaysAgoChange = (event, type) => {
    const value = event.target.value;
    if (value < 0) {
      if (type === 'min') {
        handleChangeMinDaysAgo(0);
      } else {
        handleChangeMaxDaysAgo(0);
      }
    } else if (value > 30) {
      if (type === 'min') {
        handleChangeMinDaysAgo(30);
      } else {
        handleChangeMaxDaysAgo(30);
      }
    } else {
      /* eslint-disable no-lonely-if */
      if (type === 'min') {
        handleChangeMinDaysAgo(value);
      } else {
        handleChangeMaxDaysAgo(value);
      }
    }
  };

  const handleFilterSubmit = (event) => {
    event.preventDefault();
    // Filter data based on selected filters
    if (minDaysAgo > maxDaysAgo || maxDaysAgo < minDaysAgo) {
      setError('Min days ago sold must be less than max days ago sold');
    } else {
      dispatch(
        filterRecentlySoldAsync(
          minPrice,
          maxPrice,
          minYear,
          maxYear,
          minDaysAgo,
          maxDaysAgo,
          tagFilters,
          city,
          state,
          zipCode,
          savedFilter
        )
      );
      setShowFilters(false);
    }
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
      saveFilterAsync(
        filterName,
        minPrice,
        maxPrice,
        minYear,
        maxYear,
        minDaysAgo,
        maxDaysAgo,
        tagFilters,
        city,
        state,
        zipCode,
        forZapier
      )
    );
  };
  return (
    <div className={classes.root}>
      <Stack direction="row" spacing={2} alignItems="space-between">
        <Tooltip title="Filter list">
          <IconButton onClick={() => setShowFilters(true)}>
            <Iconify icon="ic:round-filter-list" />
          </IconButton>
        </Tooltip>
        {showClearFilters && (
          <Tooltip title="Clear filters">
            <IconButton onClick={handleClearFilterButtonPressed}>
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
              {/* <Box mb={2}>
                            <Typography variant="h5">Select Filters</Typography>                        
                        </Box> */}
              <Grid container spacing={2}>
                {recentlySoldFilters && (
                  <Grid item xs={12}>
                    <FormControl component="fieldset">
                      <Typography variant="h6" mb={2}>
                        Saved Filters
                      </Typography>
                      <Grid container spacing={1}>
                        {recentlySoldFilters.map((option) => (
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
                            onChange={(event) => handleChangeZipCode(event.target.value)}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>City</InputLabel>
                          <Input type="text" value={city} onChange={(event) => handleChangeCity(event.target.value)} />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>State</InputLabel>
                          <Input
                            type="text"
                            value={state}
                            onChange={(event) => handleChangeState(event.target.value)}
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
                      <Stack direction="row" spacing={2} alignItems="center">
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
                  <Tooltip title="How long ago was the house sold, this data only goes back 30 days">
                    <Box mt={2}>
                      <Typography variant="h6" mb={2}>
                        Days Ago Sold
                      </Typography>
                      {error && (
                        <Grid item xs={12}>
                          <Typography color="error">{error}</Typography>
                        </Grid>
                      )}
                      <Stack direction="row" spacing={2} alignItems="center">
                        <FormControl fullWidth>
                          <InputLabel>Minimum</InputLabel>
                          <Input
                            type="number"
                            value={minDaysAgo}
                            onChange={(event) => handleDaysAgoChange(event, 'min')}
                          />
                        </FormControl>
                        <FormControl fullWidth>
                          <InputLabel>Maximum</InputLabel>
                          <Input
                            type="number"
                            value={maxDaysAgo}
                            onChange={(event) => handleDaysAgoChange(event, 'max')}
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
                      <Stack direction="row" spacing={2} alignItems="center">
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
                    <Typography variant="h6" mb={2}>
                      Tags
                    </Typography>
                    <Grid container spacing={1}>
                      {sortedTagOptions.map((option) => (
                        <FormControlLabel
                          key={option.value}
                          control={
                            <Checkbox
                              checked={tagFilters.includes(option.value)}
                              onChange={handleTagFilterChange}
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
