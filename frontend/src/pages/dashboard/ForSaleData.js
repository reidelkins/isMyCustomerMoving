/* eslint-disable camelcase */
import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
// material
import {
  Button,
  Box,
  Card,
  Table,
  Stack,
  LinearProgress,
  TableRow,
  TableBody,
  TableCell,
  Link,
  Container,
  Typography,
  TableContainer,
  TablePagination,
  CircularProgress,
} from '@mui/material';

import { useSelector, useDispatch } from 'react-redux';

// components
import Page from '../../components/Page';
import Scrollbar from '../../components/Scrollbar';
import SearchNotFound from '../../components/SearchNotFound';
import { ClientListHead } from '../../sections/@dashboard/client';
import Iconify from '../../components/Iconify';

import { ForSaleListToolbar } from '../../sections/@dashboard/forSale';

import ForSaleListCall from '../../redux/calls/ForSaleListCall';
import { selectForSale, getForSaleCSV } from '../../redux/actions/usersActions';
import { showLoginInfo } from '../../redux/actions/authActions';
import { makeDate } from '../../utils/makeDate';
import { handleChangePage, handleChangeRowsPerPage } from '../../utils/dataTableFunctions';
import { getComparator, applySortFilter } from '../../utils/filterFunctions';


// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'listed', label: 'Date Listed', alignRight: false },
  { id: 'address', label: 'Address', alignRight: false },
  { id: 'city', label: 'City', alignRight: false },
  { id: 'state', label: 'State', alignRight: false },
  { id: 'zipCode', label: 'Zip Code', alignRight: false },
  { id: 'price', label: 'Price', alignRight: false },
  { id: 'year_built', label: 'Year Built', alignRight: false },
];

export default function ForSaleData() {
  const dispatch = useDispatch();

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  const listForSale = useSelector(selectForSale);
  const { loading, FORSALELIST, count, forSaleFilters } = listForSale;

  const [page, setPage] = useState(0);

  const [order, setOrder] = useState('desc');

  const [orderBy, setOrderBy] = useState('listed');

  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [shownClients, setShownClients] = useState(0);

  const [csvLoading] = useState(false);

  const [forSaleLength, setForSaleLength] = useState(0);

  useEffect(() => {
    if (FORSALELIST.length < forSaleLength) {
      setPage(0);
      setShownClients(0);
    }
    setForSaleLength(FORSALELIST.length);
  }, [FORSALELIST, forSaleLength]);

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minYear, setMinYear] = useState('');
  const [maxYear, setMaxYear] = useState('');
  const [minDaysAgo, setMinDaysAgo] = useState('');
  const [maxDaysAgo, setMaxDaysAgo] = useState('');
  const [tagFilters, setTagFilters] = useState([]);
  const [zipCode, setZipCode] = useState('');
  const [city, setCity] = useState('');
  const [state, setState] = useState('');
  const [minRooms, setMinRooms] = useState('');
  const [maxRooms, setMaxRooms] = useState('');
  const [minBaths, setMinBaths] = useState('');
  const [maxBaths, setMaxBaths] = useState('');
  const [minSqft, setMinSqft] = useState('');
  const [maxSqft, setMaxSqft] = useState('');
  const [minLotSqft, setMinLotSqft] = useState('');
  const [maxLotSqft, setMaxLotSqft] = useState('');
  const [savedFilter, setSavedFilter] = useState('');
  const handleMinRoomsChange = (newMinRooms) => {
    setMinRooms(newMinRooms);
    setSavedFilter('');
  };
  const handleMaxRoomsChange = (newMaxRooms) => {
    setMaxRooms(newMaxRooms);
    setSavedFilter('');
  };
  const handleMinBathsChange = (newMinBaths) => {
    setMinBaths(newMinBaths);
    setSavedFilter('');
  };
  const handleMaxBathsChange = (newMaxBaths) => {
    setMaxBaths(newMaxBaths);
    setSavedFilter('');
  };
  const handleMinSqftChange = (newMinSqft) => {
    setMinSqft(newMinSqft);
    setSavedFilter('');
  };
  const handleMaxSqftChange = (newMaxSqft) => {
    setMaxSqft(newMaxSqft);
    setSavedFilter('');
  };
  const handleMinLotSqftChange = (newMinLotSqft) => {
    setMinLotSqft(newMinLotSqft);
    setSavedFilter('');
  };
  const handleMaxLotSqftChange = (newMaxLotSqft) => {
    setMaxLotSqft(newMaxLotSqft);
    setSavedFilter('');
  };
  const handleMinPriceChange = (newMinPrice) => {
    setMinPrice(newMinPrice);
    setSavedFilter('');
  };
  const handleMaxPriceChange = (newMaxPrice) => {
    setMaxPrice(newMaxPrice);
    setSavedFilter('');
  };
  const handleMinYearChange = (newMinYear) => {
    setMinYear(newMinYear);
    setSavedFilter('');
  };
  const handleMaxYearChange = (newMaxYear) => {
    setMaxYear(newMaxYear);
    setSavedFilter('');
  };
  const handleMinDaysAgoChange = (newMinDaysAgo) => {
    setMinDaysAgo(newMinDaysAgo);
    setSavedFilter('');
  };
  const handleMaxDaysAgoChange = (newMaxDaysAgo) => {
    setMaxDaysAgo(newMaxDaysAgo);
    setSavedFilter('');
  };
  const handleTagFiltersChange = (newTagFilters) => {
    setTagFilters(newTagFilters);
    setSavedFilter('');
  };
  const handleZipCodeChange = (newZipCode) => {
    setZipCode(newZipCode);
    setSavedFilter('');
  };
  const handleCityChange = (newCity) => {
    setCity(newCity);
    setSavedFilter('');
  };
  const handleStateChange = (newState) => {
    setState(newState);
    setSavedFilter('');
  };
  const handleSavedFilterChange = (newSavedFilter) => {
    setSavedFilter(newSavedFilter);
  };

  const exportCSV = () => {
    console.log('exporting csv');
    dispatch(
      getForSaleCSV(
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
  };

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - FORSALELIST.length) : 0;
  const filteredForSale = userInfo ? applySortFilter(FORSALELIST, getComparator(order, orderBy)) : [];
  // TODO, add val here to set length too
  useEffect(() => {
    setShownClients(count);
  }, [count]);

  return (
    <Page title="For Sale" userInfo={userInfo}>
      <Container>
        {userInfo ? <ForSaleListCall /> : null}
        {userInfo && (
          <>
            <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
              <Typography variant="h4" gutterBottom>
                Welcome {userInfo.first_name.charAt(0).toUpperCase() + userInfo.first_name.slice(1)}{' '}
                {userInfo.last_name.charAt(0).toUpperCase() + userInfo.last_name.slice(1)} 👋
              </Typography>
            </Stack>
            <Card sx={{ marginBottom: '3%' }}>
              {loading ? (
                <Box sx={{ width: '100%' }}>
                  <LinearProgress />
                </Box>
              ) : null}
              {userInfo.company.for_sale_purchased ? (
                <Scrollbar>
                  <ForSaleListToolbar
                    forSaleFilters={forSaleFilters}
                    product={userInfo.company.product.id}
                    minPrice={minPrice}
                    setMinPrice={handleMinPriceChange}
                    maxPrice={maxPrice}
                    setMaxPrice={handleMaxPriceChange}
                    minYear={minYear}
                    setMinYear={handleMinYearChange}
                    maxYear={maxYear}
                    setMaxYear={handleMaxYearChange}
                    minDaysAgo={minDaysAgo}
                    setMinDaysAgo={handleMinDaysAgoChange}
                    maxDaysAgo={maxDaysAgo}
                    setMaxDaysAgo={handleMaxDaysAgoChange}
                    tagFilters={tagFilters}
                    setTagFilters={handleTagFiltersChange}
                    zipCode={zipCode}
                    setZipCode={handleZipCodeChange}
                    city={city}
                    setCity={handleCityChange}
                    state={state}
                    setState={handleStateChange}
                    minRooms={minRooms}
                    setMinRooms={handleMinRoomsChange}
                    maxRooms={maxRooms}
                    setMaxRooms={handleMaxRoomsChange}
                    minBaths={minBaths}
                    setMinBaths={handleMinBathsChange}
                    maxBaths={maxBaths}
                    setMaxBaths={handleMaxBathsChange}
                    minSqft={minSqft}
                    setMinSqft={handleMinSqftChange}
                    maxSqft={maxSqft}
                    setMaxSqft={handleMaxSqftChange}
                    minLotSqft={minLotSqft}
                    setMinLotSqft={handleMinLotSqftChange}
                    maxLotSqft={maxLotSqft}
                    setMaxLotSqft={handleMaxLotSqftChange}
                    savedFilter={savedFilter}
                    setSavedFilter={handleSavedFilterChange}
                  />
                  <TableContainer sx={{ minWidth: 800 }}>
                    <Table>
                      <ClientListHead
                        order={order}
                        orderBy={orderBy}
                        headLabel={TABLE_HEAD}
                        rowCount={rowsPerPage}
                        numSelected={0}
                        onRequestSort={handleRequestSort}
                        onSelectAllClick={handleRequestSort}
                        checkbox={0}
                      />
                      <TableBody>
                        {filteredForSale.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                          const {
                            id,
                            address,
                            city,
                            state,
                            zip_code: zipCode,
                            listed,
                            price,
                            year_built: yearBuilt,
                          } = row;

                          return (
                            <React.Fragment key={row.id}>
                              <TableRow hover key={id} tabIndex={-1} role="checkbox">
                                <TableCell component="th" scope="row" padding="normal">
                                  <Stack direction="row" alignItems="center" spacing={2}>
                                    <Typography variant="subtitle2" noWrap>
                                      {makeDate(listed.slice(0, 10))}
                                    </Typography>
                                  </Stack>
                                </TableCell>
                                <TableCell align="left">{address}</TableCell>
                                <TableCell align="left">{city}</TableCell>
                                <TableCell align="left">{state}</TableCell>
                                <TableCell align="left">{zipCode}</TableCell>
                                <TableCell align="left">{price.toLocaleString()}</TableCell>
                                <TableCell align="left">{yearBuilt}</TableCell>
                              </TableRow>
                            </React.Fragment>
                          );
                        })}
                        {emptyRows > 0 && (
                          <TableRow style={{ height: 53 * emptyRows }}>
                            <TableCell colSpan={6} />
                          </TableRow>
                        )}
                      </TableBody>

                      {filteredForSale.length === 0 && (
                        <TableBody>
                          <TableRow>
                            <TableCell align="center" colSpan={6} sx={{ py: 3 }}>
                              <SearchNotFound searchQuery={''} tipe="client" />
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      )}
                    </Table>
                  </TableContainer>
                </Scrollbar>
              ) : (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="h5">Recently Sold Homes</Typography>
                  <Typography variant="subtitle2" gutterBottom>
                    You have not purchased this additional feature yet. You can add the option to get all for sale homes
                    in your area by clicking the button below.
                  </Typography>
                  <Button variant="contained" color="primary" aria-label="Create Company" component="label">
                    <Link
                      href={`https://billing.stripe.com/p/login/aEU2aZ4PtbdD9A49AA?prefilled_email=${userInfo.company.email}`}
                      color="secondary"
                      underline="none"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Manage Subscription
                    </Link>
                  </Button>
                </Box>
              )}
              <TablePagination
                  rowsPerPageOptions={[10, 50, 100]}
                  component="div"
                  count={shownClients}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={(event, newPage) =>
                      handleChangePage(event, newPage, setPage)
                  }
                  onRowsPerPageChange={(event) =>
                      handleChangeRowsPerPage(event, setRowsPerPage, setPage)
                  }
              />
            </Card>
            {/* TODO */}
            {csvLoading
              ? userInfo.status === 'admin' && (
                  <Button variant="contained">
                    <CircularProgress color="secondary" />
                  </Button>
                )
              : userInfo.status === 'admin' && (
                  <Button
                    onClick={exportCSV}
                    variant="contained"
                    component={RouterLink}
                    to="#"
                    startIcon={<Iconify icon="eva:plus-fill" />}
                  >
                    Download To CSV
                  </Button>
                )}
          </>
        )}
      </Container>
    </Page>
  );
}
