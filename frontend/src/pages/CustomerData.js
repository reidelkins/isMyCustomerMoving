import { filter } from 'lodash';
import { sentenceCase } from 'change-case';
import { useState, useEffect } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
// material
import {
  IconButton,
  Box,
  Card,
  Table,
  Stack,
  Button,
  Checkbox,
  LinearProgress,
  TableRow,
  TableBody,
  TableCell,
  Container,
  Typography,
  TableContainer,
  TablePagination,
  CircularProgress,
} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';

// components
import NoteModal from '../components/NoteModal';
import NewCompanyModal from '../components/NewCompanyModal';
import Page from '../components/Page';
import Label from '../components/Label';
import FileUploader from '../components/FileUploader';
import Scrollbar from '../components/Scrollbar';
import Iconify from '../components/Iconify';
import SearchNotFound from '../components/SearchNotFound';
import CounterCard from '../components/CounterCard';
import { ClientListHead, ClientListToolbar } from '../sections/@dashboard/client';

import ClientsListCall from '../redux/calls/ClientsListCall';
import { selectClients, update, updateClientAsync, serviceTitanSync, selectProgress } from '../redux/actions/usersActions';
import { logout, showLoginInfo } from '../redux/actions/authActions';

// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'name', label: 'Name', alignRight: false },
  { id: 'address', label: 'Address', alignRight: false },
  { id: 'city', label: 'City', alignRight: false },
  { id: 'state', label: 'State', alignRight: false },
  { id: 'zipCode', label: 'Zip Code', alignRight: false },
  { id: 'status', label: 'Status', alignRight: false },
  { id: 'contacted', label: 'Contacted', alignRight: false },
  { id: 'note', label: 'Note', alignRight: false },
];

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
    return filter(array, (_user) => _user.name.toLowerCase().indexOf(query.toLowerCase()) !== -1);
  }
  return stabilizedThis.map((el) => el[0]);
}

export default function CustomerData() {
  const dispatch = useDispatch();
  const navigate = useNavigate();  

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  if (!userInfo) {
    dispatch(logout());
    navigate('/login', { replace: true });
    // window.location.reload(false);
  }

  const listClient = useSelector(selectClients);
  const { loading, error, CLIENTLIST } = listClient;
  const progress = useSelector(selectProgress);

  const [page, setPage] = useState(0);
  
  const [order, setOrder] = useState('asc');

  const [selected, setSelected] = useState([]);

  const [selectedClients, setSelectedClients] = useState([]);

  const [orderBy, setOrderBy] = useState('status');

  const [filterName, setFilterName] = useState('');

  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [shownClients, setShownClients] = useState(0);
  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };
  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelecteds = CLIENTLIST.map((n) => n.name);
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
  const handleClick = (event, name, id) => {
    const selectedIndex = selected.indexOf(name);
    let newSelected = [];
    let newSelectedClients = [];
    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, name);
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
    dispatch(updateClientAsync(id, contacted, ""));
  };
  const updateStatus = () => {
    dispatch(update());
  };
  const stSync = () => {
    dispatch(serviceTitanSync());
  };

  const exportCSV = () => {
    if (CLIENTLIST.length === 0) { return }
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Name,Address,City,State,ZipCode,Status,Contacted,Note\r\n';
    CLIENTLIST.forEach((n) => {
      csvContent += `${n.name}, ${n.address}, ${n.city}, ${n.state}, ${n.zipCode}, ${n.status}, ${n.contacted}, ${n.note}\r\n`
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    const d1 = new Date().toLocaleDateString('en-US')
    const docName = `isMyCustomerMoving_${d1}`
    link.setAttribute('download', `${docName}.csv`);
    document.body.appendChild(link); // Required for FF
    link.click();
    document.body.removeChild(link);
  };
  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - CLIENTLIST.length) : 0;
  const filteredClients = userInfo ? applySortFilter(CLIENTLIST, getComparator(order, orderBy), filterName, userInfo.status) : [];
  
  const [rentCount, setRentCount] = useState(0);
  const [saleCount, setSaleCount] = useState(0);
  const [sold6Count, setSold6Count] = useState(0);
  useEffect(() => {
    let tmpRent = 0;
    let tmpSale = 0;
    let tmpSold6 = 0;
    CLIENTLIST.forEach((n) => {
      if (n.status === 'For Rent') {
        tmpRent +=  1;
      }
      if (n.status === 'For Sale') {
        tmpSale += 1;
      }
      if (n.status === 'Recently Sold (6)' || n.status === 'Recently Sold (12)') {
        tmpSold6 += 1;
      }


    });
    setRentCount(tmpRent);
    setSaleCount(tmpSale);
    setSold6Count(tmpSold6);
    if (userInfo) {
      if (userInfo.status === 'admin') {
        setShownClients(CLIENTLIST.length);
      } else {
        setShownClients(rentCount + saleCount + sold6Count);
      }
    }
  }, [CLIENTLIST, userInfo, rentCount, saleCount, sold6Count]);  
  return (
    <Page title="User">
      <Container>
        {userInfo ? <ClientsListCall /> : null}
        {userInfo && (
          <>
            <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
              <Typography variant="h4" gutterBottom>
                Welcome {(userInfo.first_name).charAt(0).toUpperCase()+(userInfo.first_name).slice(1)} {(userInfo.last_name).charAt(0).toUpperCase()+(userInfo.last_name).slice(1)} 👋
                {/* Welcome */}
              </Typography>              
              {(userInfo.email === 'reid@gmail.com' || userInfo.email === 'jb@aquaclearws.com' || userInfo.email === 'reidelkins3@gmail.com') && (
                // <Button variant="contained" component={RouterLink} to="/dashboard/adduser" startIcon={<Iconify icon="eva:plus-fill" />}>
                <NewCompanyModal/>
              )}
            </Stack>
            <Stack direction="row" alignItems="center" justifyContent="space-around" mb={5} mx={10}>
              <CounterCard
                count={saleCount}
                title="For Sale"
                // description="From buttons, to inputs, navbars, alerts or cards, you are covered"
              />
              {/* <CounterCard
                count={rentCount}
                title="For Rent"
                // description="From buttons, to inputs, navbars, alerts or cards, you are covered"
              /> */}
              <CounterCard
                count={sold6Count}
                title="Recently Sold"
                // description="From buttons, to inputs, navbars, alerts or cards, you are covered"
              />
              {/* <CounterCard
                count={sold12Count}
                title="Sold in last 6-12 months"
                // description="From buttons, to inputs, navbars, alerts or cards, you are covered"
              /> */}
            </Stack>
            <Card sx={{marginBottom:"3%"}}>
              <ClientListToolbar numSelected={selected.length} filterName={filterName} onFilterName={handleFilterByName} selectedClients={selectedClients} setSelected setSelectedClients />
              {/* {error ? (
                // <Alert severity="error">
                //   <AlertTitle>List Loading Error</AlertTitle>
                //   {error}
                // </Alert>
                logoutHandler
              ) : null} */}
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
                      rowCount={CLIENTLIST.length}
                      numSelected={selected.length}
                      onRequestSort={handleRequestSort}
                      onSelectAllClick={handleSelectAllClick}
                      checkbox={1}
                    />
                    <TableBody>
                      {filteredClients.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                        const { id, name, address, city, state, zipCode, status, contacted, note } = row;
                        const isItemSelected = selected.indexOf(name) !== -1;                        
                        
                        return (
                          <TableRow
                            hover
                            key={id}
                            tabIndex={-1}
                            role="checkbox"
                            selected={isItemSelected}
                            aria-checked={isItemSelected}
                          >
                            <TableCell padding="checkbox">
                              <Checkbox checked={isItemSelected} onChange={(event) => handleClick(event, name, id)} />
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
                              {userInfo.email !== 'demo@demo.com' ? (
                                <Label variant="ghost" color={(status === 'No Change' && 'warning') || (contacted === 'False' && 'error'  || 'success')}>
                                  {sentenceCase(status)}
                                </Label>
                              ) : (
                                <Label variant="ghost" color='warning'>
                                  Demo
                                </Label>
                              )}
                              
                            </TableCell>
                            <TableCell>
                              {(() => {
                                if (status !== 'No Change') {
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

                            {/* <TableCell align="right">
                              <UserMoreMenu />
                            </TableCell> */}
                          </TableRow>
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
                            <SearchNotFound searchQuery={filterName} />
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
            {progress.loading ? (
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

                {(userInfo.status === 'admin' && userInfo.finishedSTIntegration) && (
                  <Button onClick={stSync} variant="contained">
                    Sync With Service Titan
                  </Button>
                )}

                {(userInfo.status === 'admin') && (
                  <Button onClick={exportCSV} variant="contained" component={RouterLink} to="#" startIcon={<Iconify icon="eva:plus-fill" />}>
                    Download To CSV
                  </Button>
                )}
              </Stack>
            )}
              
              
            { userInfo.status === 'admin' && (
              <FileUploader />  
            )}
          </>
        )}
      </Container>
    </Page>
  );
}
