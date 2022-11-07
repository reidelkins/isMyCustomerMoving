import { filter } from 'lodash';
import { sentenceCase } from 'change-case';
import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
// material
import {
  IconButton,
  Box,
  Card,
  Alert,
  AlertTitle,
  Table,
  Stack,
  Button,
  Checkbox,
  TableRow,
  TableBody,
  TableCell,
  Container,
  Typography,
  TableContainer,
  TablePagination,
} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import LinearProgress from '@mui/material/LinearProgress';
import { FilePond } from 'react-filepond';
import '../filepond.css';

// components
import AnimatedModal from '../components/AnimatedModal';
import Page from '../components/Page';
import Label from '../components/Label';
import Scrollbar from '../components/Scrollbar';
import Iconify from '../components/Iconify';
import SearchNotFound from '../components/SearchNotFound';
import { UserListHead, UserListToolbar, UserMoreMenu } from '../sections/@dashboard/user';
import { DOMAIN } from '../redux/constants';

import UsersListCall from '../redux/calls/UsersListCall';
import { update, contact, users } from '../redux/actions/usersActions';

import { logout } from '../redux/actions/authActions';
import { LOGOUT } from '../redux/types/auth';





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

function getComparator(order, orderBy) {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

function applySortFilter(array, comparator, query) {
  const stabilizedThis = array.map((el, index) => [el, index]);
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

  const userLogin = useSelector((state) => state.userLogin);
  const { userInfo } = userLogin;

  const listUser = useSelector((state) => state.listUser);
  const { loading, error, USERLIST } = listUser;

  const [page, setPage] = useState(0);

  const [order, setOrder] = useState('asc');

  const [selected, setSelected] = useState([]);

  const [contacted, setContacted] = useState([]);

  const [selectedClients, setSelectedClients] = useState([]);

  const [orderBy, setOrderBy] = useState('status');

  const [filterName, setFilterName] = useState('');

  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelecteds = USERLIST.map((n) => n.name);
      setSelected(newSelecteds);
      
      const newSelectedClients = []
      for (let i=0; i < USERLIST.length; i+=1) {
        newSelectedClients.push({"address": USERLIST[i].address, "zip": USERLIST[i].zipCode})
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

  const handleContacted = (event, name) => {
    const selectedIndex = selected.indexOf(name);
    let newSelected = [];
    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, name);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
    }
    setContacted(newSelected);
    console.log(name);
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

  const updateContacted = (event, id) => {
    dispatch(contact(id))
    setTimeout(() => {dispatch(users())}, 500);
  };

  const updateStatus = () => {
    dispatch(update());
  };


  const exportCSV = () => {
    if (USERLIST.length === 0) { return }
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Name,Address,City,State,ZipCode,Status\r\n';
    USERLIST.forEach((n) => {
      csvContent += `${n.name}, ${n.address}, ${n.city}, ${n.state}, ${n.zipCode}, ${n.status}\r\n`
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

  const logoutHandler = () => {
    dispatch(logout());
    navigate('/login', { replace: true });
    window.location.reload(false);
  };

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - USERLIST.length) : 0;

  const filteredUsers = applySortFilter(USERLIST, getComparator(order, orderBy), filterName);
  // const [filteredUsers, setFilteredUsers] = useState(USERLIST)

  const isUserNotFound = filteredUsers.length === 0;

  const [files, setFiles] = useState([])

  return (
    <Page title="User">
      <Container>
        {userInfo ? <UsersListCall /> : null}
        {userInfo && (
          <>
            <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
              <Typography variant="h4" gutterBottom>
                Welcome {userInfo.name} 👋
                {/* Welcome */}
              </Typography>
              {userInfo.status === 'admin' && (
                <Button variant="contained" component={RouterLink} to="/dashboard/adduser" startIcon={<Iconify icon="eva:plus-fill" />}>
                  Add User
                </Button>
              )}
            </Stack>
            <Card sx={{marginBottom:"3%"}}>
              <UserListToolbar numSelected={selected.length} filterName={filterName} onFilterName={handleFilterByName} selectedClients={selectedClients} />
              {error ? (
                // <Alert severity="error">
                //   <AlertTitle>List Loading Error</AlertTitle>
                //   {error}
                // </Alert>
                logoutHandler
              ) : null}
              {loading ? (
                <Box sx={{ width: '100%' }}>
                  <LinearProgress />
                </Box>
              ) : null}

              <Scrollbar>
                <TableContainer sx={{ minWidth: 800 }}>
                  <Table>
                    <UserListHead
                      order={order}
                      orderBy={orderBy}
                      headLabel={TABLE_HEAD}
                      rowCount={USERLIST.length}
                      numSelected={selected.length}
                      onRequestSort={handleRequestSort}
                      onSelectAllClick={handleSelectAllClick}
                    />
                    <TableBody>
                      {filteredUsers.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
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
                              <Label variant="ghost" color={(status === 'No Change' && 'warning') || (contacted === 'False' && 'error'  || 'success')}>
                                {sentenceCase(status)}
                              </Label>
                            </TableCell>
                            <TableCell>
                              {(() => {
                                if (status !== 'No Change') {
                                  if (contacted) {
                                    return(
                                      <IconButton color="success" aria-label="View/Edit Note" component="label" onClick={(event)=>updateContacted(event, id)}>
                                        <Iconify icon="bi:check-lg" />
                                      </IconButton>
                                    )
                                  }
                                  return(
                                    <IconButton color="error" aria-label="View/Edit Note" component="label" onClick={(event)=>updateContacted(event, id)}>
                                      <Iconify icon="ps:check-box-empty" />
                                    </IconButton>
                                  )
                                }
                                
                              })()}                          
                            </TableCell>
                            <TableCell>
                              <AnimatedModal 
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

                    {isUserNotFound && (
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
                count={USERLIST.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </Card>
            <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
              <Button onClick={updateStatus} variant="contained" component={RouterLink} to="#" startIcon={<Iconify icon="eva:plus-fill" />}>
                Update Status
              </Button>

              {userInfo.status === 'admin' && (
                <Button onClick={exportCSV} variant="contained" component={RouterLink} to="#" startIcon={<Iconify icon="eva:plus-fill" />}>
                  Download To CSV
                </Button>
              )}
              
            </Stack>
            {userInfo.status === 'admin' && (
              <FilePond
                files={files}
                onupdatefiles={setFiles}
                // className="NONE"
                maxFiles={1}
                server={`${DOMAIN}/api/v1/accounts/upload/`}
                name={`${userInfo.company}`}
                labelIdle=' <span class="filepond--label-action">Upload Your Client List</span>'
                credits='false'
                storeAsFile='true'
                // acceptedFileTypes={['image/png', 'image/jpeg']}
              />
            )}
          </>
        )}
      </Container>
    </Page>
  );
}
