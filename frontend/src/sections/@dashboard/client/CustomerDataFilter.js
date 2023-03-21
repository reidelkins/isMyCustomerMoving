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
  MenuItem,
  Select,
  Typography,
  Tooltip,
  IconButton,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  Stack
} from '@mui/material';

import Iconify from '../../../components/Iconify';
import { filterClientsAsync, clientsAsync } from '../../../redux/actions/usersActions'

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
}

export default function CustomerDataFilter(product) {
    const classes = useStyles();
    const [showFilters, setShowFilters] = useState(false);
    const [statusFilters, setStatusFilters] = useState([]);
    const [minPrice, setMinPrice] = useState('');
    const [maxPrice, setMaxPrice] = useState('');
    const [minYear, setMinYear] = useState('');
    const [maxYear, setMaxYear] = useState('');
    const [tagFilters, setTagFilters] = useState([]);
    const [equipInstallDateMin, setEquipInstallDateMin] = useState('1900-01-01');
    const today = new Date();
    const [equipInstallDateMax, setEquipInstallDateMax] = useState(today.toISOString().slice(0, 10));    
    const [showClearFilters, setShowClearFilters] = useState(false);
    const dispatch = useDispatch();

    const handleTagFilterChange = (event) => {
        const { value } = event.target;
        setTagFilters((prevFilters) => {
        if (prevFilters.includes(value)) {
            return prevFilters.filter((filter) => filter !== value);
        } 
        return [...prevFilters, value];
        
        });
    };

    useEffect(() => {
        if (statusFilters.length > 0 || minPrice || maxPrice || minYear || maxYear || tagFilters.length > 0 || equipInstallDateMin || equipInstallDateMax) {
            setShowClearFilters(true);
        } else {
            setShowClearFilters(false);
        }
    }, [statusFilters, minPrice, maxPrice, minYear, maxYear, tagFilters, equipInstallDateMin, equipInstallDateMax]);

    const tagOptions = [
        { value: 'Solar', label: 'Solar' },
        { value: 'Well Water', label: 'Well Water' },
        { value: 'Residential', label: 'Residential' },
        { value: 'Pool', label: 'Pool' },
        { value: 'Commercial', label: 'Commercial' },
        { value: 'Fixer Upper', label: 'Fixer Upper' },
    ];

    const handleStatusFilterChange = (event) => {
        const { value } = event.target;
        setStatusFilters((prevFilters) => {
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
        { value: 'No Status', label: 'No Status' },
    ];

    const handleFilterSubmit = (event) => {
        event.preventDefault();
        // Filter data based on selected filters
        dispatch(filterClientsAsync(statusFilters, minPrice, maxPrice, minYear, maxYear, tagFilters, equipInstallDateMin, equipInstallDateMax))
        setShowFilters(false);
    };

    const handleShowFilters = () => {
        if (product.product === 'price_1MhxfPAkLES5P4qQbu8O45xy') {
            alert('Please upgrade your plan to access this feature')
        } else {
            setShowFilters(true)
        }
    }

    const handleClearFilters = () => {
        setStatusFilters([]);
        setMinPrice('');
        setMaxPrice('');
        setMinYear('');
        setMaxYear('');
        setTagFilters([]);
        setEquipInstallDateMax(today.toISOString().slice(0, 10));
        setEquipInstallDateMin('1900-01-01');
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
            <Dialog sx={{padding:"200px"}} className={classes.filterBox} open={showFilters} onClose={()=>(setShowFilters(false))} >
                <DialogTitle>Filter List</DialogTitle>
                <Divider />
                <DialogContent>
                <form onSubmit={handleFilterSubmit}>
                    <Box mb={2}>
                        <Typography variant="h6">Select Filters</Typography>
                        <Typography variant="body2">
                            Note: Most filters are only relevant for clients where status
                            is not "No Change"
                        </Typography>
                    </Box>
                    <Grid container spacing={2}>
                        <Tooltip title="Client Status">
                            <Grid item xs={12}>
                                {/* <FormControl fullWidth>
                                <InputLabel>Status</InputLabel>
                                <Select
                                    value={statusFilter}
                                    onChange={(event) => setStatusFilter(event.target.value)}
                                >
                                    <MenuItem value="For Sale">For Sale</MenuItem>
                                    <MenuItem value="Recently Sold">Recently Sold</MenuItem>
                                    <MenuItem value="Off Market">Off Market</MenuItem>
                                    <MenuItem value="Off Market">No Status</MenuItem>
                                </Select>
                                </FormControl> */}
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
                            <Tooltip title="This will filter for the price that the house was either sold or listed for">
                                <Box mt={2}>
                                    <Typography variant="h6" mb={2}>Housing Price</Typography>
                                    <Stack direction="row" spacing={2} alignItems="space-between">
                                        <FormControl fullWidth>
                                            <InputLabel>Min Price</InputLabel>
                                            <Input
                                                type="number"
                                                value={minPrice}
                                                onChange={(event) => setMinPrice(event.target.value)}
                                            />
                                        </FormControl>
                                        <FormControl fullWidth>
                                        <InputLabel>Max Price</InputLabel>
                                        <Input
                                            type="number"
                                            value={maxPrice}
                                            onChange={(event) => setMaxPrice(event.target.value)}
                                        />
                                        </FormControl>
                                    </Stack>
                                </Box>
                            </Tooltip>
                        </Grid>
                        <Grid item xs={12}>
                            <Tooltip title="Time range that the equipment was installed at the location for the client">
                                <Box mt={2}>
                                    <Typography variant="h6" mb={2}>Equipment Installation Date</Typography>
                                    <Stack direction="row" spacing={2} alignItems="space-between">
                                        <FormControl fullWidth>
                                            <InputLabel>Earliest</InputLabel>
                                            <Input
                                                type="date"
                                                defaultValue={equipInstallDateMin}
                                                value={equipInstallDateMin}
                                                onChange={(event) => setEquipInstallDateMin(event.target.value)}
                                            />
                                        </FormControl>
                                    
                                        <FormControl fullWidth>
                                            <InputLabel>Latest</InputLabel>
                                            <Input
                                                type="date"
                                                defaultValue={equipInstallDateMax}
                                                value={equipInstallDateMax}
                                                onChange={(event) => setEquipInstallDateMax(event.target.value)}
                                            />
                                        </FormControl>
                                    </Stack>
                                </Box>
                            </Tooltip>
                        </Grid>
                        
                        <Grid item xs={12}>
                            <Tooltip title="Year the house was built">
                                <Box mt={2}>
                                    <Typography variant="h6" mb={2}>Year Built</Typography>
                                    <Stack direction="row" spacing={2} alignItems="space-between">
                                        <FormControl fullWidth>
                                            <InputLabel>Min Year Built</InputLabel>
                                            <Input
                                                type="number"
                                                value={minYear}
                                                onChange={(event) => setMinYear(event.target.value)}
                                            />
                                        </FormControl>
                                        <FormControl fullWidth>
                                            <InputLabel>Max Year Built</InputLabel>
                                            <Input
                                                type="number"
                                                value={maxYear}
                                                onChange={(event) => setMaxYear(event.target.value)}
                                            />
                                        </FormControl>
                                    </Stack>
                                </Box>
                            </Tooltip>
                        </Grid>                        
                    {/* <Grid item xs={12}>
                        <FormControl component="fieldset">
                        <FormLabel component="legend">Tags</FormLabel>
                        <Grid container spacing={1}>
                            {tagOptions.map((option) => (
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
                    </Grid> */}
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
    )
}