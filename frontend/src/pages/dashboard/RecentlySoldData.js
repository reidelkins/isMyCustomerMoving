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

import { RecentlySoldListToolbar } from '../../sections/@dashboard/recentlySold';

import RecentlySoldListCall from '../../redux/calls/RecentlySoldListCall';
import { selectRecentlySold, getRecentlySoldCSV } from '../../redux/actions/usersActions';
import { showLoginInfo } from '../../redux/actions/authActions';
import { makeDate } from '../../utils/makeDate';
import { handleChangePage, handleChangeRowsPerPage, handleRequestSort } from '../../utils/dataTableFunctions';
import { getComparator, applySortFilter } from '../../utils/filterFunctions';


// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'listed', label: 'Date Sold', alignRight: false },
  { id: 'address', label: 'Address', alignRight: false },
  { id: 'city', label: 'City', alignRight: false },
  { id: 'state', label: 'State', alignRight: false },
  { id: 'zipCode', label: 'Zip Code', alignRight: false },
  { id: 'price', label: 'Price', alignRight: false },
  { id: 'year_built', label: 'Year Built', alignRight: false },
  { id: 'tags', label: 'Tags', alignRight: false },
];


export default function RecentlySoldData() {
  const dispatch = useDispatch();

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  const listRecentlySold = useSelector(selectRecentlySold);
  const { loading, RECENTLYSOLDLIST, count, recentlySoldFilters } = listRecentlySold;

  const [page, setPage] = useState(0);

  const [order, setOrder] = useState('desc');

  const [orderBy, setOrderBy] = useState('listed');

  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [shownClients, setShownClients] = useState(0);

  const [csvLoading] = useState(false);

  const [recentlySoldLength, setRecentlySoldLength] = useState(0);

  useEffect(() => {
    if (RECENTLYSOLDLIST.length < recentlySoldLength) {
      setPage(0);
      setShownClients(0);
    }
    setRecentlySoldLength(RECENTLYSOLDLIST.length);
  }, [RECENTLYSOLDLIST, recentlySoldLength]);

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
    dispatch(
      getRecentlySoldCSV(
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

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - RECENTLYSOLDLIST.length) : 0;
  const filteredRecentlySold = userInfo ? applySortFilter(RECENTLYSOLDLIST, getComparator(order, orderBy)) : [];
  // TODO, add val here to set length too
  useEffect(() => {
    setShownClients(count);
  }, [count]);

  const tagColors = [  '#E57373',  '#81C784',  '#64B5F6', '#FFC107', '#BA68C8'];
  function capitalizeWords(str) {
    return str.replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
  }
  return (
    <Page title="Recently Sold" userInfo={userInfo}>
      <Container>
        {userInfo ? <RecentlySoldListCall /> : null}
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
              {userInfo.company.recently_sold_purchased ? (
                <Scrollbar>
                  <RecentlySoldListToolbar
                    recentlySoldFilters={recentlySoldFilters}
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
                        onRequestSort={(event, property) => handleRequestSort(event, property, orderBy, order, setOrder, setOrderBy)}
                        onSelectAllClick={handleRequestSort}
                        checkbox={0}
                      />
                      <TableBody>
                        {filteredRecentlySold.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                          const {
                            id,
                            address,
                            city,
                            state,
                            zip_code: zipCode,
                            listed,
                            price,
                            year_built: yearBuilt,
                            tags
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
                                <TableCell align="left">{price ? price.toLocaleString() : "$0"}</TableCell>
                                <TableCell align="left">{yearBuilt}</TableCell>
                                <TableCell align="left">
                                  {tags && tags.map((tag, index) => (
                                    <span 
                                        key={tag} 
                                        style={{
                                            backgroundColor: tagColors[index % tagColors.length],
                                            color: 'white',
                                            borderRadius: '15px',
                                            padding: '5px 10px',
                                            margin: '5px 2px',
                                            display: 'inline-block',
                                            fontWeight: 'bold'
                                        }}
                                    >
                                        {capitalizeWords(tag)}
                                    </span>
                                ))}
                                </TableCell>
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

                      {filteredRecentlySold.length === 0 && (
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
                    You have not purchased this additional feature yet. You can add the option to get all recently sold
                    homes in your area by clicking the button below.
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
