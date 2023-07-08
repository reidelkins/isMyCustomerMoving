/* eslint-disable camelcase */
import { sentenceCase } from 'change-case';
import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
// material
import {
  Alert,
  IconButton,
  Box,
  Card,
  Collapse,
  Table,
  Stack,
  Button,
  Checkbox,
  LinearProgress,
  TableRow,
  TableBody,
  TableCell,
  Tooltip,
  Container,
  Typography,
  TableContainer,
  TablePagination,
  CircularProgress,
} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { applySortFilter, getComparator } from '../../utils/filterFunctions';

// components
import IncorrectDataButton from '../../components/IncorrectDataButton';
import RemoveErrorFlagButton from '../../components/RemoveErrorFlagButton';
import ReferralModal from '../../components/ReferralModal';
import UpgradeFromFree from '../../components/UpgradeFromFree';
import NoteModal from '../../components/NoteModal';
import Page from '../../components/Page';
import Label from '../../components/Label';
import FileUploader from '../../components/FileUploader';
import Scrollbar from '../../components/Scrollbar';
import Iconify from '../../components/Iconify';
import SearchNotFound from '../../components/SearchNotFound';
import CounterCard from '../../components/CounterCard';
import ClientEventTable from '../../components/ClientEventTable';
import ClientDetailsTable from '../../components/ClientDetailsTable';
import ServiceTitanSyncModal from '../../components/ServiceTitanSyncModal';
import Map from '../../components/Map';
import { ClientListHead, ClientListToolbar } from '../../sections/@dashboard/client';

import ClientsListCall from '../../redux/calls/ClientsListCall';
import {
  selectClients,
  update,
  updateClientAsync,
  salesForceSync,
  getClientsCSV,
} from '../../redux/actions/usersActions';
import { showLoginInfo } from '../../redux/actions/authActions';

import '../../theme/map.css';

export default function HomePage() {
  const dispatch = useDispatch();

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  const [TABLE_HEAD, setTABLE_HEAD] = useState([
    { id: 'name', label: 'Name', alignRight: false },
    { id: 'address', label: 'Address', alignRight: false },
    { id: 'city', label: 'City', alignRight: false },
    { id: 'state', label: 'State', alignRight: false },
    { id: 'zipCode', label: 'Zip Code', alignRight: false },
    { id: 'status', label: 'Status', alignRight: false },
    { id: 'contacted', label: 'Contacted', alignRight: false },
    { id: 'note', label: 'Note', alignRight: false },
    { id: 'phone', label: 'Phone Number', alignRight: false },
  ]);
  useEffect(() => {
    if (
      (userInfo && userInfo.company.enterprise) ||
      userInfo.email === 'reid@gmail.com' ||
      userInfo.email === 'reid@ismycustomermoving.com' ||
      userInfo.email === 'jb@aquaclearws.com'
    ) {
      setTABLE_HEAD([
        { id: 'serviceTitanCustomerSinceYear', label: 'Customer Since', alignRight: false },
        { id: 'name', label: 'Name', alignRight: false },
        { id: 'address', label: 'Address', alignRight: false },
        { id: 'city', label: 'City', alignRight: false },
        { id: 'state', label: 'State', alignRight: false },
        { id: 'zipCode', label: 'Zip Code', alignRight: false },
        { id: 'status', label: 'Status', alignRight: false },
        { id: 'contacted', label: 'Contacted', alignRight: false },
        { id: 'note', label: 'Note', alignRight: false },
        { id: 'phone', label: 'Phone Number', alignRight: false },
        { id: 'referral', label: 'Refer', alignRight: false },
      ]);
    } else if (userInfo && userInfo.company.crm === 'ServiceTitan') {
      setTABLE_HEAD([
        { id: 'serviceTitanCustomerSinceYear', label: 'Customer Since', alignRight: false },
        { id: 'name', label: 'Name', alignRight: false },
        { id: 'address', label: 'Address', alignRight: false },
        { id: 'city', label: 'City', alignRight: false },
        { id: 'state', label: 'State', alignRight: false },
        { id: 'zipCode', label: 'Zip Code', alignRight: false },
        { id: 'status', label: 'Status', alignRight: false },
        { id: 'contacted', label: 'Contacted', alignRight: false },
        { id: 'note', label: 'Note', alignRight: false },
        { id: 'phone', label: 'Phone Number', alignRight: false },
      ]);
    }
  }, [userInfo]);

  const listClient = useSelector(selectClients);
  const { loading, CLIENTLIST, forSale, recentlySold, count, message, deleted, customerDataFilters } = listClient;
  useEffect(() => {
    if (message) {
      setAlertOpen(true);
    }
  }, [message]);

  const [page, setPage] = useState(0);

  const [order, setOrder] = useState('asc');

  const [selected, setSelected] = useState([]);

  const [selectedClients, setSelectedClients] = useState([]);

  const [orderBy, setOrderBy] = useState('status');

  const [filterName, setFilterName] = useState('');

  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [shownClients, setShownClients] = useState(0);

  const [expandedRow, setExpandedRow] = useState(null);

  const [csvLoading] = useState(false);

  const [alertOpen, setAlertOpen] = useState(false);

  const [deletedAlertOpen, setDeletedAlertOpen] = useState(false);

  useEffect(() => {
    if (deleted > 0) {
      setDeletedAlertOpen(true);
    }
  }, [deleted]);

  const [clientListLength, setClientListLength] = useState(0);

  const [filteredClients, setFilteredClients] = useState([]);

  useEffect(() => {
    if (CLIENTLIST.length > 0) {
      setFilteredClients(applySortFilter(CLIENTLIST, getComparator(order, orderBy), filterName, userInfo.status));
    } else {
      setFilteredClients([]);
    }
  }, [CLIENTLIST, order, orderBy, filterName, userInfo]);

  useEffect(() => {
    if (CLIENTLIST.length < clientListLength) {
      setPage(0);
      setShownClients(0);
    }
    setClientListLength(CLIENTLIST.length);
  }, [CLIENTLIST, clientListLength, CLIENTLIST.length]);

  const handleRowClick = (rowIndex) => {
    if (expandedRow === rowIndex) {
      setExpandedRow(null);
    } else {
      setExpandedRow(rowIndex);
    }
  };

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };
  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelecteds = CLIENTLIST.slice(page * rowsPerPage, (page + 1) * rowsPerPage).map((n) => n.address);
      setSelected(newSelecteds);

      const newSelectedClients = [];
      for (let i = 0; i < CLIENTLIST.length; i += 1) {
        newSelectedClients.push(CLIENTLIST[i].id);
      }
      setSelectedClients(newSelectedClients);
      return;
    }
    setSelected([]);
    setSelectedClients([]);
  };

  const handleClick = (event, address, id) => {
    const selectedIndex = selected.indexOf(address);
    let newSelected = [];
    let newSelectedClients = [];
    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, address);
      newSelectedClients = newSelectedClients.concat(selectedClients, id);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
      newSelectedClients = newSelectedClients.concat(selectedClients.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
      newSelectedClients = newSelectedClients.concat(selectedClients.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
      newSelectedClients = newSelectedClients.concat(
        selectedClients.slice(0, selectedIndex),
        selectedClients.slice(selectedIndex + 1)
      );
    }
    setSelected(newSelected);
    setSelectedClients(newSelectedClients);
  };
  const handleChangePage = (event, newPage) => {
    // fetch new page if two away from needing to see new page
    // if (((newPage + 2) * rowsPerPage) % 1000 === 0) {
    //   dispatch(clientsAsync(((newPage + 2) * rowsPerPage) / 1000 + 1));
    // }
    setPage(newPage);
  };
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  const handleFilterByName = (event) => {
    setFilterName(event.target.value);
  };
  const updateContacted = (event, id, contacted) => {
    dispatch(updateClientAsync(id, contacted, '', '', '', ''));
  };
  const updateStatus = () => {
    dispatch(update());
  };
  const sfSync = () => {
    dispatch(salesForceSync());
  };

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - CLIENTLIST.length) : 0;

  useEffect(() => {
    if (filteredClients.length < CLIENTLIST.length) {
      setShownClients(filteredClients.length);
    } else {
      setShownClients(count);
    }
  }, [count, filteredClients, CLIENTLIST.length]);

  const [statusFilters, setStatusFilters] = useState([]);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minYear, setMinYear] = useState('');
  const [maxYear, setMaxYear] = useState('');
  const [tagFilters, setTagFilters] = useState([]);
  const [equipInstallDateMin, setEquipInstallDateMin] = useState('');
  const [equipInstallDateMax, setEquipInstallDateMax] = useState('');
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
  const [customerSinceMin, setCustomerSinceMin] = useState('');
  const [customerSinceMax, setCustomerSinceMax] = useState('');
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
  const handleStatusFiltersChange = (newFilters) => {
    setStatusFilters(newFilters);
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
  const handleEquipInstallDateMin = (newEquipInstallDateMin) => {
    setEquipInstallDateMin(newEquipInstallDateMin);
    setSavedFilter('');
  };
  const handleEquipInstallDateMax = (newEquipInstallDateMax) => {
    setEquipInstallDateMax(newEquipInstallDateMax);
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
  const handleTagFiltersChange = (newTagFilters) => {
    setTagFilters(newTagFilters);
    setSavedFilter('');
  };
  const handleCustomerSinceMin = (newCustomerSinceMin) => {
    setCustomerSinceMin(newCustomerSinceMin);
    setSavedFilter('');
  };
  const handleCustomerSinceMax = (newCustomerSinceMax) => {
    setCustomerSinceMax(newCustomerSinceMax);
    setSavedFilter('');
  };
  const handleSavedFilterChange = (newSavedFilter) => {
    setSavedFilter(newSavedFilter);
  };

  const exportCSV = () => {
    dispatch(
      getClientsCSV(
        statusFilters,
        minPrice,
        maxPrice,
        minYear,
        maxYear,
        tagFilters,
        equipInstallDateMin,
        equipInstallDateMax,
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

  const [listOrMap, setListOrMap] = useState('list');
  const handleListOrMap = (newListOrMap) => {
    setListOrMap(newListOrMap);
  };

  return (
    <div>
      {userInfo && (
        <Page title="User" userInfo={userInfo}>
          <Container>
            {userInfo ? <ClientsListCall /> : null}
            {userInfo && (
              <>
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                  <Typography variant="h4" gutterBottom>
                    Welcome {userInfo.first_name.charAt(0).toUpperCase() + userInfo.first_name.slice(1)}{' '}
                    {userInfo.last_name.charAt(0).toUpperCase() + userInfo.last_name.slice(1)} 👋
                  </Typography>
                </Stack>
                <Stack direction="row" alignItems="center" justifyContent="center" mb={5}>
                  <Typography variant="h3" gutterBottom>
                    {userInfo.company.name}
                  </Typography>
                </Stack>
                <Stack direction="row" alignItems="center" justifyContent="space-around" mb={5} mx={10}>
                  <Stack direction="column" alignItems="center" justifyContent="center">
                    <CounterCard start={0} end={forSale.current} title="For Sale" />
                    <Typography variant="h6" gutterBottom mt={-3}>
                      {' '}
                      All Time: {forSale.total}
                    </Typography>
                  </Stack>

                  <Stack direction="column" alignItems="center" justifyContent="center">
                    <CounterCard start={0} end={recentlySold.current} title="Recently Sold" />
                    <Typography variant="h6" gutterBottom mt={-3}>
                      {' '}
                      All Time: {recentlySold.total}
                    </Typography>
                  </Stack>
                </Stack>
                <Card sx={{ marginBottom: '3%' }}>
                  <ClientListToolbar
                    numSelected={selected.length}
                    filterName={filterName}
                    onFilterName={handleFilterByName}
                    selectedClients={selectedClients}
                    setSelected
                    setSelectedClients
                    product={userInfo.company.product.id}
                    customerDataFilters={customerDataFilters}
                    minPrice={minPrice}
                    setMinPrice={handleMinPriceChange}
                    maxPrice={maxPrice}
                    setMaxPrice={handleMaxPriceChange}
                    minYear={minYear}
                    setMinYear={handleMinYearChange}
                    maxYear={maxYear}
                    setMaxYear={handleMaxYearChange}
                    equipInstallDateMin={equipInstallDateMin}
                    setEquipInstallDateMin={handleEquipInstallDateMin}
                    equipInstallDateMax={equipInstallDateMax}
                    setEquipInstallDateMax={handleEquipInstallDateMax}
                    statusFilters={statusFilters}
                    setStatusFilters={handleStatusFiltersChange}
                    listOrMap={listOrMap}
                    setListOrMap={handleListOrMap}
                    tagFilters={tagFilters}
                    setTagFilters={handleTagFiltersChange}
                    zipCode={zipCode}
                    setZipCode={handleZipCodeChange}
                    city={city}
                    setCity={handleCityChange}
                    state={state}
                    setState={handleStateChange}
                    customerSinceMin={customerSinceMin}
                    setCustomerSinceMin={handleCustomerSinceMin}
                    customerSinceMax={customerSinceMax}
                    setCustomerSinceMax={handleCustomerSinceMax}
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
                  {loading ? (
                    <Box sx={{ width: '100%' }}>
                      <LinearProgress />
                    </Box>
                  ) : null}
                  {listOrMap === 'list' ? (
                    <>
                      <Scrollbar>
                        <TableContainer sx={{ minWidth: 800 }}>
                          <Table>
                            <ClientListHead
                              order={order}
                              orderBy={orderBy}
                              headLabel={TABLE_HEAD}
                              rowCount={rowsPerPage}
                              numSelected={selected.length}
                              onRequestSort={handleRequestSort}
                              onSelectAllClick={handleSelectAllClick}
                              checkbox={1}
                            />
                            <TableBody>
                              {filteredClients
                                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                .map((row) => {
                                  const {
                                    id,
                                    name,
                                    address,
                                    city,
                                    state,
                                    zip_code: zipCode,
                                    status,
                                    contacted,
                                    note,
                                    phone_number: phoneNumber,
                                    client_updates_client: clientUpdates,
                                    price,
                                    year_built: yearBuilt,
                                    housing_type: housingType,
                                    equipment_installed_date: equipmentInstalledDate,
                                    error_flag: errorFlag,
                                    service_titan_customer_since_year: serviceTitanCustomerSinceYear,
                                  } = row;
                                  const isItemSelected = selected.indexOf(address) !== -1;

                                  return (
                                    <React.Fragment key={row.id}>
                                      <Tooltip title="Click For Expanded Details">
                                        <TableRow
                                          hover
                                          key={id}
                                          tabIndex={-1}
                                          role="checkbox"
                                          selected={isItemSelected}
                                          aria-checked={isItemSelected}
                                          onClick={() => handleRowClick(id)}
                                        >
                                          <TableCell padding="checkbox">
                                            <Checkbox
                                              checked={isItemSelected}
                                              onChange={(event) => handleClick(event, address, id)}
                                            />
                                          </TableCell>
                                          {userInfo.company.crm === 'ServiceTitan' && (
                                            <TableCell component="th" scope="row" padding="none">
                                              <Label variant="ghost" color="info">
                                                {serviceTitanCustomerSinceYear !== 1
                                                  ? serviceTitanCustomerSinceYear
                                                  : '1900'}
                                              </Label>
                                            </TableCell>
                                          )}
                                          <TableCell component="th" scope="row" padding="none">
                                            <Stack direction="row" alignItems="center" spacing={2}>
                                              <Typography variant="subtitle2" noWrap>
                                                {name}
                                              </Typography>
                                            </Stack>
                                          </TableCell>
                                          <TableCell align="left">{address}</TableCell>
                                          <TableCell align="left">{city}</TableCell>
                                          <TableCell align="left">{state}</TableCell>
                                          <TableCell align="left">{zipCode}</TableCell>
                                          <TableCell align="left">
                                            {userInfo.company.product.id !== 'price_1MhxfPAkLES5P4qQbu8O45xy' ? (
                                              <Label
                                                variant="ghost"
                                                color={
                                                  (status === 'No Change' && 'warning') ||
                                                  (contacted === 'False' && 'error') ||
                                                  'success'
                                                }
                                              >
                                                {status === 'No Change' ? 'Off Market' : sentenceCase(status)}
                                              </Label>
                                            ) : (
                                              <Label variant="ghost" color="warning">
                                                Free Tier
                                              </Label>
                                            )}
                                          </TableCell>
                                          <TableCell>
                                            {(() => {
                                              if (
                                                status !== 'No Change' &&
                                                userInfo.company.product.id !== 'price_1MhxfPAkLES5P4qQbu8O45xy'
                                              ) {
                                                if (contacted) {
                                                  return (
                                                    <IconButton
                                                      color="success"
                                                      aria-label="Contacted"
                                                      component="label"
                                                      onClick={(event) => updateContacted(event, id, false)}
                                                    >
                                                      <Iconify icon="bi:check-lg" />
                                                    </IconButton>
                                                  );
                                                }
                                                return (
                                                  <IconButton
                                                    color="error"
                                                    aria-label="Not Contacted"
                                                    component="label"
                                                    onClick={(event) => updateContacted(event, id, true)}
                                                  >
                                                    <Iconify icon="ps:check-box-empty" />
                                                  </IconButton>
                                                );
                                              }
                                              return null;
                                            })()}
                                          </TableCell>
                                          <TableCell>
                                            <NoteModal passedNote={note} id={id} name={name} />
                                          </TableCell>
                                          <TableCell>
                                            {/* make phone number look like (123) 456-7890 */}
                                            {phoneNumber
                                              ? `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(
                                                  3,
                                                  6
                                                )}-${phoneNumber.slice(6, 10)}`
                                              : 'N/A'}
                                          </TableCell>

                                          {(userInfo.company.enterprise ||
                                            userInfo.email === 'reid@gmail.com' ||
                                            userInfo.email === 'reid@ismycustomermoving.com' ||
                                            userInfo.email === 'jb@aquaclearws.com') && (
                                            <TableCell>
                                              {(() => {
                                                if (status !== 'No Change') {
                                                  return <ReferralModal id={id} alreadyReferred={false} />;
                                                }
                                                return null;
                                              })()}
                                            </TableCell>
                                          )}
                                        </TableRow>
                                      </Tooltip>
                                      {expandedRow === id &&
                                        userInfo.company.product.id !== 'price_1MhxfPAkLES5P4qQbu8O45xy' && (
                                          <TableRow style={{ position: 'relative', left: '10%' }}>
                                            <TableCell colSpan={6}>
                                              <Stack
                                                direction="row"
                                                alignItems="center"
                                                justifyContent="space-between"
                                                mb={5}
                                              >
                                                <ClientEventTable clientUpdates={clientUpdates} />
                                                <ClientDetailsTable
                                                  price={price}
                                                  yearBuilt={yearBuilt}
                                                  housingType={housingType}
                                                  equipmentInstalledDate={equipmentInstalledDate}
                                                />
                                                {errorFlag ? (
                                                  <RemoveErrorFlagButton clientId={id} />
                                                ) : (
                                                  <IncorrectDataButton clientId={id} />
                                                )}
                                              </Stack>
                                            </TableCell>
                                          </TableRow>
                                        )}
                                    </React.Fragment>
                                  );
                                })}
                              {emptyRows > 0 && (
                                <TableRow style={{ height: 53 * emptyRows }}>
                                  <TableCell colSpan={6} />
                                </TableRow>
                              )}
                            </TableBody>

                            {filteredClients.length === 0 && (
                              <TableBody>
                                <TableRow>
                                  <TableCell align="center" colSpan={6} sx={{ py: 3 }}>
                                    <SearchNotFound searchQuery={filterName} tipe="client" />
                                  </TableCell>
                                </TableRow>
                              </TableBody>
                            )}
                          </Table>
                        </TableContainer>
                      </Scrollbar>

                      <TablePagination
                        rowsPerPageOptions={[10, 50, 100]}
                        component="div"
                        count={shownClients}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                      />
                    </>
                  ) : (
                    <Map clients={filteredClients} />
                  )}
                </Card>
                <Collapse in={deletedAlertOpen}>
                  <Alert
                    action={
                      <IconButton
                        aria-label="close"
                        color="inherit"
                        size="small"
                        onClick={() => {
                          setDeletedAlertOpen(false);
                        }}
                      >
                        X
                      </IconButton>
                    }
                    sx={{ mb: 2, mx: 'auto', width: '80%' }}
                    variant="filled"
                    severity="error"
                  >
                    You tried to upload {deleted} clients more than allowed for your subscription tier. If you would
                    like to upload more clients, please upgrade your subscription.
                  </Alert>
                </Collapse>
                {loading ? (
                  <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                    {((userInfo.first_name === 'reid' && userInfo.last_name === 'elkins') ||
                      (userInfo.first_name === 'Perspective' && userInfo.last_name === 'Customer')) && (
                      <Button variant="contained">
                        <CircularProgress color="secondary" />
                      </Button>
                    )}

                    {userInfo.status === 'admin' && userInfo.finished_st_integration && (
                      <Button variant="contained">
                        <CircularProgress color="secondary" />
                      </Button>
                    )}

                    {userInfo.status === 'admin' && (
                      <Button variant="contained">
                        <CircularProgress color="secondary" />
                      </Button>
                    )}
                  </Stack>
                ) : (
                  <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                    {((userInfo.first_name === 'reid' && userInfo.last_name === 'elkins') ||
                      (userInfo.first_name === 'Perspective' && userInfo.last_name === 'Customer')) && (
                      <Button
                        onClick={updateStatus}
                        variant="contained"
                        component={RouterLink}
                        to="#"
                        startIcon={<Iconify icon="eva:plus-fill" />}
                      >
                        Update Status
                      </Button>
                    )}

                    {userInfo.status === 'admin' &&
                      (userInfo.company.crm === 'ServiceTitan' ? (
                        <ServiceTitanSyncModal
                          serviceTitanCustomerSyncOption={userInfo.company.service_titan_customer_sync_option}
                        />
                      ) : (
                        userInfo.company.crm === 'Salesforce' && (
                          <Button onClick={sfSync} variant="contained">
                            Sync With Salesforce
                          </Button>
                        )
                      ))}
                    {csvLoading
                      ? userInfo.status === 'admin' && (
                          <Button variant="contained">
                            <CircularProgress color="secondary" />
                          </Button>
                        )
                      : userInfo.status === 'admin' &&
                        userInfo.company.product.id !== 'price_1MhxfPAkLES5P4qQbu8O45xy' && (
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
                    {userInfo.company.product.id === 'price_1MhxfPAkLES5P4qQbu8O45xy' && <UpgradeFromFree />}
                  </Stack>
                )}

                {userInfo.status === 'admin' && <FileUploader />}

                <Collapse in={alertOpen}>
                  <Alert
                    action={
                      <IconButton
                        aria-label="close"
                        color="inherit"
                        size="small"
                        onClick={() => {
                          setAlertOpen(false);
                        }}
                      >
                        X
                      </IconButton>
                    }
                    sx={{ mb: 2, mx: 'auto', width: '50%' }}
                    variant="filled"
                    severity="success"
                  >
                    {message}
                  </Alert>
                </Collapse>
              </>
            )}
          </Container>
        </Page>
      )}
    </div>
  );
}
