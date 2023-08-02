import React, { useState, useEffect } from 'react';
import { sentenceCase } from 'change-case';
import { Link as RouterLink } from 'react-router-dom';
import { 
    Box,
    Button, 
    Card,
    Checkbox,
    CircularProgress,
    LinearProgress,
    IconButton,
    Stack,
    Table, 
    TableBody,
    TableCell,
    TableRow,
    TableContainer,
    TablePagination,
    Tooltip,
    Typography,
} from '@mui/material';
import { useDispatch } from 'react-redux';
import PropTypes from 'prop-types';

import Label from './Label';
import Scrollbar from './Scrollbar';
import SearchNotFound from './SearchNotFound';
import Map from './Map';
import IncorrectDataButton from './IncorrectDataButton';
import RemoveErrorFlagButton from './RemoveErrorFlagButton';
import ClientDetailsTable from './ClientDetailsTable';
import ClientEventTable from './ClientEventTable';
import Iconify from './Iconify';
import ReferralModal from './ReferralModal';
import NoteModal from './NoteModal';
import ServiceTitanSyncModal from './ServiceTitanSyncModal';
import UpgradeFromFree from './UpgradeFromFree';
import { ClientListHead, ClientListToolbar } from '../sections/@dashboard/client';
import { getClientsCSV, salesForceSync,  updateClientAsync, update, updateCounts } from '../redux/actions/usersActions';
import { applySortFilter, getComparator } from '../utils/filterFunctions';
import { handleChangePage, handleChangeRowsPerPage, handleRequestSort } from '../utils/dataTableFunctions';

const commonFields = [
  { id: 'name', label: 'Name', alignRight: false },
  { id: 'address', label: 'Address', alignRight: false },
  { id: 'city', label: 'City', alignRight: false },
  { id: 'state', label: 'State', alignRight: false },
  { id: 'zipCode', label: 'Zip Code', alignRight: false },
  { id: 'status', label: 'Status', alignRight: false },
  { id: 'contacted', label: 'Contacted', alignRight: false },
  { id: 'note', label: 'Note', alignRight: false },
  { id: 'phone', label: 'Phone Number', alignRight: false },
];

CustomerData.propTypes = {
    userInfo: PropTypes.object,
    CLIENTLIST: PropTypes.array,
    loading: PropTypes.bool,
    customerDataFilters: PropTypes.array,
    count: PropTypes.number,
};

export default function CustomerData({ userInfo, CLIENTLIST, loading, customerDataFilters, count}) {
    const [TABLE_HEAD, setTableHead] = useState(commonFields);
    useEffect(() => {
        const updatedFields = [...commonFields];

        if (userInfo && userInfo.company.crm === 'ServiceTitan') {
        updatedFields.unshift({ id: 'serviceTitanLifetimeRevenue', label: 'Lifetime Revenue', alignRight: false });
        updatedFields.unshift({ id: 'serviceTitanCustomerSinceYear', label: 'Customer Since', alignRight: false });        
        }
        if (userInfo && (userInfo.company.enterprise || userInfo.email === 'reid@gmail.com' ||
        userInfo.email === 'reid@ismycustomermoving.com' ||
        userInfo.email === 'jb@aquaclearws.com')) {
        updatedFields.push({ id: 'referral', label: 'Refer', alignRight: false });
        }

        setTableHead(updatedFields);

    }, [userInfo]);
    const [csvLoading] = useState(false);
    const dispatch = useDispatch();
    const [listOrMap, setListOrMap] = useState('list');
    const handleListOrMap = (newListOrMap) => {
        setListOrMap(newListOrMap);
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
    
    const [filterName, setFilterName] = useState('');
    const handleFilterByName = (event) => {
        setFilterName(event.target.value);
    };
    const updateContacted = (event, id, contacted, status) => {
        dispatch(updateClientAsync(id, contacted, '', '', '', ''));
        const updatedClients = filteredClients.map((client) =>
            client.id === id ? { ...client, contacted } : client
        );
        dispatch(updateCounts(contacted, status, updatedClients));

        setFilteredClients(applySortFilter(updatedClients, getComparator(order, orderBy), filterName, userInfo.status));
    };
    
    const handleRowClick = (rowIndex) => {
        if (expandedRow === rowIndex) {
        setExpandedRow(null);
        } else {
        setExpandedRow(rowIndex);
        }
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
    const [orderBy, setOrderBy] = useState('status');
    const [order, setOrder] = useState('asc');
    const [expandedRow, setExpandedRow] = useState(null);
    const [filteredClients, setFilteredClients] = useState([]);
    useEffect(() => {
        if (CLIENTLIST.length > 0) {
        setFilteredClients(applySortFilter(CLIENTLIST, getComparator(order, orderBy), filterName, userInfo.status));
        } else {
        setFilteredClients([]);
        }
    }, [CLIENTLIST, order, orderBy, filterName, userInfo]);    
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
    const [uspsChanged, setUspsChanged] = useState(false);
    const handleUspsChange = () => {
        setUspsChanged(!uspsChanged);
        setSavedFilter('');
    };
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
    const [selected, setSelected] = useState([]);
    const [selectedClients, setSelectedClients] = useState([]);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [shownClients, setShownClients] = useState(0);
    const [clientListLength, setClientListLength] = useState(0);
    useEffect(() => {
        if (CLIENTLIST.length < clientListLength) {
        setPage(0);
        setShownClients(0);
        }
        setClientListLength(CLIENTLIST.length);
    }, [CLIENTLIST, clientListLength, CLIENTLIST.length]);
    useEffect(() => {
        if (filteredClients.length < CLIENTLIST.length) {
        setShownClients(filteredClients.length);
        } else {
        setShownClients(count);
        }
    }, [count, filteredClients, CLIENTLIST.length]);
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
            savedFilter,
            uspsChanged
        )
        );
    };
    const updateStatus = () => {
      dispatch(update());
    };
    const sfSync = () => {
      dispatch(salesForceSync());
    };
    const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - CLIENTLIST.length) : 0;
    return (
        <>
            <Card sx={{ marginBottom: '3%' }} data-testid="customer-data-card">
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
                    uspsChanged={uspsChanged}
                    setUspsChanged={handleUspsChange}
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
                            <Table data-testid="customer-data-table">
                                <ClientListHead
                                order={order}
                                orderBy={orderBy}
                                headLabel={TABLE_HEAD}
                                rowCount={rowsPerPage}
                                numSelected={selected.length}
                                onRequestSort={(event, property) => handleRequestSort(event, property, orderBy, order, setOrder, setOrderBy)}
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
                                        service_titan_lifetime_revenue: serviceTitanLifetimeRevenue,
                                    } = row;
                                    const isItemSelected = selected.indexOf(address) !== -1;

                                    return (
                                        <React.Fragment key={row.id}>
                                        <Tooltip title="Click For Expanded Details" placement="right">
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
                                                <>
                                                    <TableCell component="th" scope="row" padding="none">
                                                        <Label variant="ghost" color="info">
                                                            {serviceTitanCustomerSinceYear !== 1
                                                            ? serviceTitanCustomerSinceYear
                                                            : '1900'}
                                                        </Label>
                                                    </TableCell>
                                                    <TableCell component="th" scope="row" padding="none">
                                                        <Label variant="ghost" color="info">
                                                            ${Math.floor(serviceTitanLifetimeRevenue)}
                                                        </Label>
                                                    </TableCell>
                                                </>
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
                                                        onClick={(event) => updateContacted(event, id, false, status)}
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
                                                        onClick={(event) => updateContacted(event, id, true, status)}
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
                            onPageChange={(event, newPage) =>
                                handleChangePage(event, newPage, setPage)
                            }
                            onRowsPerPageChange={(event) =>
                                handleChangeRowsPerPage(event, setRowsPerPage, setPage)
                            }
                        />
                    </>
                ) : (
                    <Map clients={filteredClients} />
                )}
            </Card>
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
        </>
    )
}
