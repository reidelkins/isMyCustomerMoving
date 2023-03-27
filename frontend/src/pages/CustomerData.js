/* eslint-disable camelcase */
import _, { filter} from 'lodash';
import axios from 'axios';
import { sentenceCase } from 'change-case';
import React, { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
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
import { useAuth0 } from "@auth0/auth0-react";

import { DOMAIN, URL } from '../redux/constants';

// components
import ReferralModal from '../components/ReferralModal';
import UpgradeFromFree from '../components/UpgradeFromFree';
import NoteModal from '../components/NoteModal';
import Page from '../components/Page';
import Label from '../components/Label';
import FileUploader from '../components/FileUploader';
import Scrollbar from '../components/Scrollbar';
import Iconify from '../components/Iconify';
import SearchNotFound from '../components/SearchNotFound';
import CounterCard from '../components/CounterCard';
import ClientEventTable from '../components/ClientEventTable';
import ClientDetailsTable from '../components/ClientDetailsTable';
import { ClientListHead, ClientListToolbar } from '../sections/@dashboard/client';

import ClientsListCall from '../redux/calls/ClientsListCall';
import { selectClients, update, updateClientAsync, serviceTitanSync, salesForceSync, clientsAsync } from '../redux/actions/usersActions';
import { getUser, showLoginInfo } from '../redux/actions/authActions';

// ----------------------------------------------------------------------
// change this to sort by status
function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

export function getComparator(order, orderBy) {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

export function applySortFilter(array, comparator, query, userInfo) {
  let stabilizedThis = array;  
  if (userInfo === 'admin') {
    stabilizedThis = array.map((el, index) => [el, index]);
  } else {
    stabilizedThis = array.filter(el => el.status !== 'No Change').map((el, index) => [el, index]);
  }
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  if (query) {
    return filter(array, (_user) => _.some(_user, val=>val && val.toString().toLowerCase().includes(query.toLowerCase())));;
  }
  return stabilizedThis.map((el) => el[0]);
}

export default function CustomerData() {
  const dispatch = useDispatch();
  const { getAccessTokenSilently } = useAuth0();
  const [accessToken, setAccessToken] = useState(null);

  useEffect(() => {
    const fetchAccessToken = async () => {
      const token = await getAccessTokenSilently();
      setAccessToken(token);
    };

    fetchAccessToken();

    // return a cleanup function to cancel any pending async operation and prevent updating the state on an unmounted component
    return () => {
      setAccessToken(null);
    };
  }, [getAccessTokenSilently]);

  const userLogin = useSelector(showLoginInfo);
  const { userInfo, error } = userLogin;
  const { user, isAuthenticated, isLoading, logout } = useAuth0();

  useEffect(() => {
    // TODO figure out how to set an error that lasts
    if (error) {
      console.log('error', error)
      // logout({
      //   logoutParams: {
      //     returnTo: `${URL}/login/error`,
      //     state: 'error=NoUserWithThatEmail'
      //   },
      // });
    }
  }, [error]);

  useEffect(async () => {
    if (isAuthenticated && accessToken) {      
      dispatch(getUser(user.email, accessToken));
    }
  }, [isAuthenticated, user, accessToken]);
  
  
  const [TABLE_HEAD, setTABLE_HEAD] = useState([{ id: 'name', label: 'Name', alignRight: false },
        { id: 'address', label: 'Address', alignRight: false },
        { id: 'city', label: 'City', alignRight: false },
        { id: 'state', label: 'State', alignRight: false },
        { id: 'zipCode', label: 'Zip Code', alignRight: false },
        { id: 'status', label: 'Status', alignRight: false },
        { id: 'contacted', label: 'Contacted', alignRight: false },
        { id: 'note', label: 'Note', alignRight: false },
        { id: 'phone', label: 'Phone Number', alignRight: false }]);
  useEffect(() => {
    if (userInfo && userInfo.company.franchise) {
      setTABLE_HEAD([
        { id: 'name', label: 'Name', alignRight: false },
        { id: 'address', label: 'Address', alignRight: false },
        { id: 'city', label: 'City', alignRight: false },
        { id: 'state', label: 'State', alignRight: false },
        { id: 'zipCode', label: 'Zip Code', alignRight: false },
        { id: 'status', label: 'Status', alignRight: false },
        { id: 'contacted', label: 'Contacted', alignRight: false },
        { id: 'note', label: 'Note', alignRight: false },
        { id: 'phone', label: 'Phone Number', alignRight: false },
        { id: 'referral', label: 'Refer', alignRight: false }
      ]);
    }
  }, [userInfo]);

  const listClient = useSelector(selectClients);
  const {loading, CLIENTLIST, forSale, recentlySold, count, message, deleted } = listClient;
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

  const [csvLoading, setCsvLoading] = useState(false);

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
    }
  }, [CLIENTLIST, order, orderBy, filterName, userInfo]);

  useEffect(() => {
    if (CLIENTLIST.length < clientListLength) {
      setPage(0);
      setShownClients(0);      
    }
    setClientListLength(CLIENTLIST.length);
  }, [CLIENTLIST]);

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

      const newSelecteds = CLIENTLIST.slice((page * rowsPerPage), ((page+1) * rowsPerPage)).map((n) => n.address);
      setSelected(newSelecteds);
      
      const newSelectedClients = []
      for (let i=0; i < CLIENTLIST.length; i+=1) {
        newSelectedClients.push(CLIENTLIST[i].id)
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
      newSelectedClients = newSelectedClients.concat(selectedClients.slice(0, selectedIndex), selectedClients.slice(selectedIndex + 1));
    }
    setSelected(newSelected);
    setSelectedClients(newSelectedClients);

  };
  const handleChangePage = (event, newPage) => {
    // fetch new page if two away from needing to see new page
    if ((newPage+2) * rowsPerPage % 1000 === 0) {
      dispatch(clientsAsync( ((newPage+2) * rowsPerPage / 1000)+1, accessToken))
    }
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
    dispatch(updateClientAsync(id, contacted, "", accessToken));
  };
  const updateStatus = () => {
    dispatch(update(accessToken));
  };
  const stSync = () => {
    dispatch(serviceTitanSync(accessToken));
  };
  const sfSync = () => {
    dispatch(salesForceSync(accessToken));
  };

  const exportCSV = async () => {
    if (CLIENTLIST.length === 0) { return }
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    setCsvLoading(true);
    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/allClients/${userInfo.id}`, config);
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Name,Address,City,State,ZipCode,Status,Contacted,Note,Phone Number\r\n';
    data.forEach((n) => {
      csvContent += `${n.name}, ${n.address}, ${n.city}, ${n.state}, ${n.zipCode}, ${n.status}, ${n.contacted}, ${n.note}, ${n.phoneNumber}\r\n`
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    // Create a download link for the CSV file
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    const d1 = new Date().toLocaleDateString('en-US')
    const docName = `isMyCustomerMoving_${d1}`    

    link.setAttribute('download', `${docName}.csv`);
    document.body.appendChild(link); // add the link to body
    link.click();
    document.body.removeChild(link); // remove the link from body
    setCsvLoading(false);
  };
  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - CLIENTLIST.length) : 0;
  
  
  useEffect(() => {
    if (filteredClients.length < CLIENTLIST.length) {
      setShownClients(filteredClients.length)
    } else {
      setShownClients(count)
    }
  }, [count, filteredClients])
  

  if (isLoading) {
      console.log("loading");
      return <div>Loading ...</div>;
    }
  
  
  return (
    <div>
    {isAuthenticated && userInfo && (
      <Page title="User" userInfo={userInfo}>
        <Container>
          {userInfo ? <ClientsListCall /> : null}
          {userInfo && (
            <>
              <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                <Typography variant="h4" gutterBottom>
                  Welcome {(userInfo.first_name).charAt(0).toUpperCase()+(userInfo.first_name).slice(1)} {(userInfo.last_name).charAt(0).toUpperCase()+(userInfo.last_name).slice(1)} 👋
                </Typography>              
                {/* {(userInfo.email === 'reid@gmail.com' || userInfo.email === 'jb@aquaclearws.com' || userInfo.email === 'reidelkins3@gmail.com') && (
                  // <Button variant="contained" component={RouterLink} to="/dashboard/adduser" startIcon={<Iconify icon="eva:plus-fill" />}>
                  <NewCompanyModal/>
                )} */}
              </Stack>
              <Stack direction="row" alignItems="center" justifyContent="space-around" mb={5} mx={10}>
                <Stack direction="column" alignItems="center" justifyContent="center">
                  <CounterCard
                    start={0}
                    end={forSale.current}
                    title="For Sale"
                  />
                  <Typography variant="h6" gutterBottom mt={-3}> All Time: {forSale.total}</Typography>
                </Stack>

                <Stack direction="column" alignItems="center" justifyContent="center">
                  <CounterCard
                    start={0}
                    end={recentlySold.current}
                    title="Recently Sold"
                  />
                  <Typography variant="h6" gutterBottom mt={-3}> All Time: {recentlySold.total}</Typography>
                </Stack>
              </Stack>
              <Card sx={{marginBottom:"3%"}}>
                <ClientListToolbar numSelected={selected.length} filterName={filterName} onFilterName={handleFilterByName} selectedClients={selectedClients} setSelected setSelectedClients product={userInfo.company.product} />
                {loading ? (
                  <Box sx={{ width: '100%' }}>
                    <LinearProgress />
                  </Box>
                ) : null}

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
                        {filteredClients.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                          const { id, name, address, city, state, zipCode, status, contacted, note, phoneNumber, clientUpdates_client: clientUpdates, price, year_built: yearBuilt, housingType, equipmentInstalledDate} = row;
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
                                    <Checkbox checked={isItemSelected} onChange={(event) => handleClick(event, address, id)} />
                                  </TableCell>
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
                                    {userInfo.company.product !== 'price_1MhxfPAkLES5P4qQbu8O45xy' ? (
                                      <Label variant="ghost" color={(status === 'No Change' && 'warning') || (contacted === 'False' && 'error'  || 'success')}>
                                        {sentenceCase(status)}
                                      </Label>
                                    ) : (
                                      <Label variant="ghost" color='warning'>
                                        Free Tier
                                      </Label>
                                    )}
                                    
                                  </TableCell>
                                  <TableCell>
                                    {(() => {
                                      if (status !== 'No Change' && userInfo.company.product !== 'price_1MhxfPAkLES5P4qQbu8O45xy') {
                                        if (contacted) {
                                          return(
                                            <IconButton color="success" aria-label="View/Edit Note" component="label" onClick={(event)=>updateContacted(event, id, false)}>
                                              <Iconify icon="bi:check-lg" />
                                            </IconButton>
                                          )
                                        }
                                        return(
                                          <IconButton color="error" aria-label="View/Edit Note" component="label" onClick={(event)=>updateContacted(event, id, true)}>
                                            <Iconify icon="ps:check-box-empty" />
                                          </IconButton>
                                        )
                                      }
                                      return null;                                
                                    })()}                          
                                  </TableCell>
                                  <TableCell>
                                    <NoteModal 
                                      passedNote={note}
                                      id={id}
                                      name={name}
                                    />
                                  </TableCell>
                                  <TableCell>
                                    {/* make phone number look like (123) 456-7890 */}
                                    {phoneNumber ? `(${phoneNumber.slice(0,3)}) ${phoneNumber.slice(3,6)}-${phoneNumber.slice(6,10)}`: "N/A"}
                                  </TableCell>
                                  {userInfo.company.franchise && (
                                    <TableCell>
                                      {(() => {
                                        if (status !== 'No Change') {
                                          return(
                                            <ReferralModal id={id} alreadyReferred={false}/>
                                          )
                                        }
                                        return null;                                
                                      })()}                          
                                    </TableCell>
                                  )}
                                  
                                </TableRow>
                              </Tooltip>                                                                         
                              {expandedRow === id && userInfo.company.product !== 'price_1MhxfPAkLES5P4qQbu8O45xy' && (
                                <TableRow style={{position:'relative', left:'10%'}}>
                                  <TableCell colSpan={6}>
                                    <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                                      <ClientEventTable clientUpdates={clientUpdates}/>                                     
                                      <ClientDetailsTable price={price} yearBuilt={yearBuilt} housingType={housingType} equipmentInstalledDate={equipmentInstalledDate} />                                    
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
                              <SearchNotFound searchQuery={filterName} tipe="client"/>
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
                  You tried to upload {deleted} clients more than allowed for your subscription tier. If you would like to upload more clients, please upgrade your subscription.
                </Alert>
              </Collapse>
              {loading ? (
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                  {((userInfo.first_name === 'reid' && userInfo.last_name === 'elkins') || (userInfo.first_name === 'Perspective' && userInfo.last_name === 'Customer')) && (
                    <Button variant="contained" >
                      <CircularProgress color="secondary"/>
                    </Button>
                  )  }            

                  {(userInfo.status === 'admin' && userInfo.finishedSTIntegration) && (
                    <Button variant="contained">
                      <CircularProgress color="secondary"/>
                    </Button>
                  )}

                  {(userInfo.status === 'admin') && (
                    <Button variant="contained">
                      <CircularProgress color="secondary"/>
                    </Button>
                  )}
                </Stack>

              ):(
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
                  {((userInfo.first_name === 'reid' && userInfo.last_name === 'elkins') || (userInfo.first_name === 'Perspective' && userInfo.last_name === 'Customer')) && (
                    <Button onClick={updateStatus} variant="contained" component={RouterLink} to="#" startIcon={<Iconify icon="eva:plus-fill" />}>
                      Update Status
                    </Button>
                  )}        

                  {userInfo.status === 'admin' && (                 
                    (
                      userInfo.company.crm === 'ServiceTitan' ? (
                        <Button onClick={stSync} variant="contained">
                          Sync With Service Titan
                        </Button>
                      )
                      :
                    (
                      userInfo.company.crm === 'Salesforce' && (
                        <Button onClick={sfSync} variant="contained">
                          Sync With Salesforce
                        </Button>
                      )
                    ))                  
                  )}
                  {csvLoading ? (
                    (userInfo.status === 'admin') && (
                      <Button variant="contained">
                        <CircularProgress color="secondary"/>
                      </Button>
                    )
                  ):(
                    (userInfo.status === 'admin' && userInfo.company.product !== 'price_1MhxfPAkLES5P4qQbu8O45xy') && (
                      <Button onClick={exportCSV} variant="contained" component={RouterLink} to="#" startIcon={<Iconify icon="eva:plus-fill" />}>
                        Download To CSV
                      </Button>
                    )
                  )}
                  {userInfo.company.product === 'price_1MhxfPAkLES5P4qQbu8O45xy' && (
                    <UpgradeFromFree />
                  )}
                  
                </Stack>
              )}
                                        
              { userInfo.status === 'admin' && (
                  <FileUploader />
              )}
              
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
    )
    }
    </div>
  );
}
