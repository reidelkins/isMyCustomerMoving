import React, { useState } from 'react';
import { useDispatch } from 'react-redux';

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
} from '@mui/material';

import Iconify from '../../../components/Iconify';
import { filterRecentlySoldAsync } from '../../../redux/actions/usersActions'

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




export default function RecentlySoldDataFilter() {
    const classes = useStyles();
    const [showFilters, setShowFilters] = useState(false);
    const [minPrice, setMinPrice] = useState('');
    const [maxPrice, setMaxPrice] = useState('');
    const [minYear, setMinYear] = useState('');
    const [maxYear, setMaxYear] = useState('');
    const [tagFilters, setTagFilters] = useState([]);
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

    const tagOptions = [
        { value: 'Solar', label: 'Solar' },
        { value: 'Well Water', label: 'Well Water' },
        { value: 'Residential', label: 'Residential' },
        { value: 'Pool', label: 'Pool' },
        { value: 'Commercial', label: 'Commercial' },
        { value: 'Fixer Upper', label: 'Fixer Upper' },
    ];

    const handleFilterSubmit = (event) => {
        event.preventDefault();
        // Filter data based on selected filters
        dispatch(filterRecentlySoldAsync(minPrice, maxPrice, minYear, maxYear, tagFilters))
        setMinPrice('');
        setMaxPrice('');
        setMinYear('');
        setMaxYear('');
        setTagFilters([]);
        setShowFilters(false);
        console.log("sup sup sup")
    };

    return (
        <div className={classes.root}>
            <Tooltip title="Filter list">
                <IconButton onClick={()=>setShowFilters(true)}>
                    <Iconify icon="ic:round-filter-list" />
                </IconButton>
            </Tooltip>
            {showFilters && (
            <Dialog sx={{padding:"200px"}} className={classes.filterBox} open={showFilters} onClose={()=>(setShowFilters(false))} >
                <DialogTitle>Filter List</DialogTitle>
                <Divider />
                <DialogContent>
                <form onSubmit={handleFilterSubmit}>
                    <Box mb={2}>
                        <Typography variant="h6">Select Filters</Typography>                        
                    </Box>
                    <Grid container spacing={2}>                        
                        <Grid item xs={6}>
                            <FormControl fullWidth>
                            <InputLabel>Min Price</InputLabel>
                            <Input
                                type="number"
                                value={minPrice}
                                onChange={(event) => setMinPrice(event.target.value)}
                            />
                            </FormControl>
                        </Grid>
                    <Grid item xs={6}>
                        <FormControl fullWidth>
                        <InputLabel>Max Price</InputLabel>
                        <Input
                            type="number"
                            value={maxPrice}
                            onChange={(event) => setMaxPrice(event.target.value)}
                        />
                        </FormControl>
                    </Grid>
                    <Grid item xs={6}>
                        <FormControl fullWidth>
                        <InputLabel>Min Year Built</InputLabel>
                        <Input
                            type="number"
                            value={minYear}
                            onChange={(event) => setMinYear(event.target.value)}
                        />
                        </FormControl>
                    </Grid>
                    <Grid item xs={6}>
                        <FormControl fullWidth>
                        <InputLabel>Max Year Built</InputLabel>
                        <Input
                            type="number"
                            value={maxYear}
                            onChange={(event) => setMaxYear(event.target.value)}
                        />
                        </FormControl>
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