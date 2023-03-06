import React, { useState } from 'react';

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




export default function CustomerDataFilter() {
    const classes = useStyles();
    const [showFilters, setShowFilters] = useState(false);
    const [statusFilter, setStatusFilter] = useState('');
    const [minPrice, setMinPrice] = useState('');
    const [maxPrice, setMaxPrice] = useState('');
    const [minYear, setMinYear] = useState('');
    const [maxYear, setMaxYear] = useState('');
    const [tagFilters, setTagFilters] = useState([]);

    const handleTagFilterChange = (event) => {
        const { value } = event.target;
        setTagFilters((prevFilters) => {
        if (prevFilters.includes(value)) {
            return prevFilters.filter((filter) => filter !== value);
        } 
        return [...prevFilters, value];
        
        });
    };

    const handleFilterSubmit = (event) => {
        event.preventDefault();
        // Filter data based on selected filters
        console.log({
        status: statusFilter,
        minPrice,
        maxPrice,
        minYear,
        maxYear,
        tags: tagFilters,
        });
        setShowFilters(false);
    };
    return (
        <div className={classes.root}>
            <Tooltip title="Filter list">
                {/* <IconButton onClick={() => setShowFilters(!showFilters)}>
                    <Iconify icon="ic:round-filter-list" />
                </IconButton> */}
                <IconButton>
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
                        <Typography variant="body2">
                            Note: Most filters are only relevant for clients where status
                            is not "No Change"
                        </Typography>
                    </Box>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <FormControl fullWidth>
                            <InputLabel>Status</InputLabel>
                            <Select
                                value={statusFilter}
                                onChange={(event) => setStatusFilter(event.target.value)}
                            >
                                <MenuItem value="">All</MenuItem>
                                <MenuItem value="For Sale">For Sale</MenuItem>
                                <MenuItem value="Recently Sold">Recently Sold</MenuItem>
                                <MenuItem value="Off Market">Off Market</MenuItem>
                            </Select>
                            </FormControl>
                        </Grid>
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
                    <Grid item xs={12}>
                        <FormControl component="fieldset">
                        <FormLabel component="legend">Tags</FormLabel>
                        <Grid container spacing={1}>
                            <Grid item xs={4}>
                            <FormControlLabel
                                control={
                                <Checkbox
                                    value="Tag 1"
                                    checked={tagFilters.includes('Tag 1')}
                                    onChange={handleTagFilterChange}
                                />
                                }
                                label="Tag 1"
                            />
                            </Grid>
                            <Grid item xs={4}>
                            <FormControlLabel
                                control={
                                <Checkbox
                                    value="Tag 2"
                                    checked={tagFilters.includes('Tag 2')}
                                    onChange={handleTagFilterChange}
                                />
                                }
                                label="Tag 2"
                            />
                            </Grid>
                            <Grid item xs={4}>
                            <FormControlLabel
                                control={
                                <Checkbox
                                    value="Tag 3"
                                    checked={tagFilters.includes('Tag 3')}
                                    onChange={handleTagFilterChange}
                                />
                                }
                                label="Tag 3"
                            />
                            </Grid>
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
    )
}