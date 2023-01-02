/* eslint-disable camelcase */
/* eslint-disable no-nested-ternary */

import {useState} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import * as Yup from 'yup';
import { useFormik } from 'formik';
import { useNavigate } from 'react-router-dom';

import { Box, Checkbox, LinearProgress, Link, TextField, Card, Grid, Container, Typography, Stack, Button, TableContainer, Table, TableBody, TableCell, TableRow, IconButton } from '@mui/material';

// components
import Iconify from '../components/Iconify';
import Page from '../components/Page';
import Scrollbar from '../components/Scrollbar';
import { UserListHead, UserListToolbar } from '../sections/@dashboard/user';
import NewUserModal from '../components/NewUserModal';
import IntegrateSTModal from '../components/IntegrateSTModal';
import AddSecretModal from '../components/AddSecretModal';
import { applySortFilter, getComparator } from './CustomerData';
// import ResetPasswordModal from '../components/ResetPasswordModal';

import UsersListCall from '../redux/calls/UsersListCall';
import { showLoginInfo, logout } from '../redux/actions/authActions';
import { manageUser, selectUsers, makeAdminAsync } from '../redux/actions/usersActions';


// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'employee', label: 'Name', alignRight: false },
  { id: 'email', label: 'Email', alignRight: false },
  { id: 'role', label: 'Status', alignRight: false },
  // { id: 'status', label: 'Account Created', alignRight: false },
];

export default function ProfileSettings() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;
  const [editting, setEditting] = useState(false);

  const listUser = useSelector(selectUsers);
  const { loading, error, USERLIST } = listUser;

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [filterName, setFilterName] = useState('');
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('status');
  const adminBool = userInfo.status === 'admin' ? 1 : 0;

  const handleFilterByName = (event) => {
    setFilterName(event.target.value);
  };

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - USERLIST.length) : 0;

  const filteredUsers = applySortFilter(USERLIST, getComparator(order, orderBy), filterName);

  const SettingsSchema = Yup.object().shape({
    name: Yup.string().required('Name is required'),
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
    servTitan: Yup.string(),
  });

  const formik = useFormik({
    initialValues: {
      name: userInfo.name,
      email: userInfo.email,
      servTitan: userInfo.company.tenantID,
    },
    validationSchema: SettingsSchema,
    onSubmit: () => {
      // TODO
      console.log(values.servTitan)
    },
  });

  const { errors, touched, values, getFieldProps } = formik;


  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const save = () => {
    setEditting(false);  
  };

  const logoutHandler = () => {
    dispatch(logout());
    navigate('/login', { replace: true });
  };

  const sendReminder = (event, email) => {
    dispatch(manageUser(email));
  };

  const makeAdmin = (event, userId) => {
    dispatch(makeAdminAsync(userId));
  };

  const [selected, setSelected] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);

  const handleClick = (event, id) => {
    const selectedIndex = selected.indexOf(id);
    let newSelected = [];
    let newSelectedUsers = [];
    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, id);
      newSelectedUsers = newSelectedUsers.concat(selectedUsers, id);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
      newSelectedUsers = newSelectedUsers.concat(selectedUsers.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
      newSelectedUsers = newSelectedUsers.concat(selectedUsers.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(selected.slice(0, selectedIndex), selected.slice(selectedIndex + 1));
      newSelectedUsers = newSelectedUsers.concat(selectedUsers.slice(0, selectedIndex), selectedUsers.slice(selectedIndex + 1));
    }
    setSelected(newSelected);
    setSelectedUsers(newSelectedUsers);

  };

  return (
    <Page title="Profile Settings">
      <Container maxWidth="xl">
        {userInfo ? <UsersListCall /> : null}
        <Typography variant="h2" sx={{ mb: 5 }}>
          User Settings
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={8}>
            {editting ? (
                <Stack direction='column'>
                  <h3>Name:</h3>
                  <TextField
                    fullWidth                                        
                    type="text"  
                    {...getFieldProps('name')}
                    error={Boolean(touched.name && errors.name)}
                    helperText={touched.name && errors.name}
                  />
                  <br />
                  <h3>Email:</h3>
                  <TextField
                    fullWidth                    
                    type="email"
                    {...getFieldProps('email')}
                    error={Boolean(touched.email && errors.email)}
                    helperText={touched.email && errors.email}
                  />
                  <br />
                  <h3>Service Titan Tenant ID:</h3>
                  {adminBool ? (                    
                    <TextField
                      fullWidth
                      type="text"  
                      {...getFieldProps('servTitan')}
                      error={Boolean(touched.servTitan && errors.servTitan)}
                      helperText={touched.servTitan && errors.servTitan}
                    />
                  ) : (
                    userInfo.company.tenantID ? <p>{userInfo.company.tenantID}</p> : <IntegrateSTModal userInfo={userInfo} />                    
                  )}
                  <br />
                  <Button variant="contained" onClick={save} >Save</Button>             
                </Stack>
              ):(
                <Stack direction='column'>
                  <h3>Name:</h3>
                  <p>{userInfo.name}</p>
                  <br />
                  <h3>Email:</h3>
                  <p>{userInfo.email}</p>
                  <br />
                  <h3>Service Titan Tenant ID:</h3>                  
                  {userInfo.company.tenantID ? <p>{userInfo.company.tenantID}</p> : <IntegrateSTModal userInfo={userInfo} />}
                  {(!userInfo.company.clientID && userInfo.company.tenantID) && <AddSecretModal userInfo={userInfo}/>}
                  <br />
                  <Button variant="contained" onClick={()=>(setEditting(true))} >Edit</Button>             
                </Stack>
                
              )}            
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            {" "}
          </Grid>
        </Grid>
        <Card sx={{marginTop:"3%", marginBottom:"3%", padding:'3%'}}>
          <UserListToolbar numSelected={selected.length} filterName={filterName} onFilterName={handleFilterByName} selectedUsers={selectedUsers} setSelected setSelectedUsers/>
          { error ? (                
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
                  headLabel={TABLE_HEAD}
                  checkbox={adminBool}
                  order={order}
                  orderBy={orderBy}
                  rowCount={0}
                  numSelected={0}
                  onRequestSort={handleRequestSort}
                />
                <TableBody>
                  {filteredUsers.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                    const { id, first_name, last_name, email, status } = row;
                    const isItemSelected = selected.indexOf(id) !== -1;
                    if (email !== 'reid@gmail.com' && email !== 'reidelkins3@gmail.com') {
                      return (
                        <TableRow
                          hover
                          key={id}
                          tabIndex={-1}>
                          {adminBool ? (
                            <TableCell padding="checkbox">
                              <Checkbox checked={isItemSelected} onChange={(event) => handleClick(event, id)}/>
                            </TableCell>    
                            ) : null
                          }
                                          
                          <TableCell component="th" scope="row" padding="none">
                            <Stack direction="row" alignItems="center" spacing={2}>
                              <Typography variant="subtitle2" noWrap>
                                {first_name} {last_name}
                              </Typography>
                            </Stack>
                          </TableCell>
                          <TableCell align="left">{email}</TableCell>
                          <TableCell align="left">
                            {status}{}                          
                          </TableCell>
                          <TableCell align="left">
                            {(() => {
                              if (status === 'pending' && adminBool) {
                                return(
                                  <Button  aria-label="Send Reminder" component="label" onClick={(event)=>sendReminder(event, email)}>
                                    &nbsp;&nbsp;&nbsp;Send Reminder
                                  </Button>
                                )
                              } 
                              if (status === 'active' && adminBool) {
                                return(
                                  <Button  aria-label="Make Admin" component="label" onClick={(event)=>makeAdmin(event, id)}>
                                    &nbsp;&nbsp;&nbsp;Make Admin
                                  </Button>
                                )
                              }
                            })()}
                          </TableCell>
                          <TableCell>
                            <h1>{userInfo.role}</h1>
                          </TableCell>
                        </TableRow>
                      );
                    }                  
                    return null;                    
                  })}
                  {emptyRows > 0 && (
                    <TableRow style={{ height: 53 * emptyRows }}>
                      <TableCell colSpan={6} />
                    </TableRow>
                  )}
                </TableBody>                
              </Table>
            </TableContainer>
          </Scrollbar>
        </Card>
        {/* <ResetPasswordModal /> */}
        { adminBool ? (
          <>
            <NewUserModal />
            <br/>
            <Button variant="contained" color="primary" aria-label="Create Company" component="label">
                <Link href="https://billing.stripe.com/p/login/aEU2aZ4PtbdD9A49AA" color="secondary" underline="none" >
                  Manage Subscription
                </Link>
            </Button>
          </>       
        ) : null}
                           
      </Container>
    </Page>
  );
}
