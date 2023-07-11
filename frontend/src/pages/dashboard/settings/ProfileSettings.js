/* eslint-disable camelcase */
/* eslint-disable no-nested-ternary */

import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import * as Yup from 'yup';
import { useFormik, Form, FormikProvider } from 'formik';
import {
  Box,
  Checkbox,
  LinearProgress,
  Link,
  TextField,
  Card,
  Grid,
  Container,
  Typography,
  Stack,
  Button,
  TableContainer,
  Table,
  TableBody,
  TableCell,
  TableRow,
} from '@mui/material';

// components
// import Iconify from '../components/Iconify';
import Page from '../../../components/Page';
import Scrollbar from '../../../components/Scrollbar';
import { UserListHead, UserListToolbar } from '../../../sections/@dashboard/user';
import NewUserModal from '../../../components/NewUserModal';

import TwoFactorAuth from '../../../components/TwoFactorAuth';
import CRMIntegrationModal from '../../../components/CRMIntegrationModal';
import UpgradeFromFree from '../../../components/UpgradeFromFree';
import { applySortFilter, getComparator } from '../../../utils/filterFunctions';
// import ResetPasswordModal from '../components/ResetPasswordModal';

import UsersListCall from '../../../redux/calls/UsersListCall';
import { showLoginInfo, editUserAsync } from '../../../redux/actions/authActions';
import { addUser, selectUsers, makeAdminAsync } from '../../../redux/actions/usersActions';

// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'employee', label: 'Name', alignRight: false },
  { id: 'email', label: 'Email', alignRight: false },
  { id: 'status', label: 'Status', alignRight: false },
  // { id: 'status', label: 'Account Created', alignRight: false },
];

export default function ProfileSettings() {
  const dispatch = useDispatch();
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  const [editting, setEditting] = useState(false);

  const listUser = useSelector(selectUsers);
  const { loading, USERLIST } = listUser;

  // const [page, setPage] = useState(0);
  const page = 0;
  // const [rowsPerPage, setRowsPerPage] = useState(10);
  const rowsPerPage = 10;
  const [filterName, setFilterName] = useState('');
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('status');
  const adminBool = userInfo && userInfo.status === 'admin' ? 1 : 0;

  const handleFilterByName = (event) => {
    setFilterName(event.target.value);
  };

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - USERLIST.length) : 0;

  const filteredUsers = applySortFilter(USERLIST, getComparator(order, orderBy), filterName);

  const SettingsSchema = Yup.object().shape({
    firstName: Yup.string().required('Name is required'),
    lastName: Yup.string().required('Name is required'),
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
    phone: Yup.string(),
  });

  const formik = useFormik({
    initialValues: {
      firstName: userInfo ? userInfo.first_name : '',
      lastName: userInfo ? userInfo.last_name : '',
      email: userInfo ? userInfo.email : '',
      phone: userInfo ? userInfo.phone : '',
    },
    validationSchema: SettingsSchema,
    onSubmit: () => {
      setEditting(false);
      dispatch(editUserAsync(values.email, values.firstName, values.lastName, values.servTitan, values.phone));
    },
  });

  const { errors, touched, values, handleSubmit, getFieldProps } = formik;

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sendReminder = (event, email) => {
    dispatch(addUser(email));
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
      newSelectedUsers = newSelectedUsers.concat(
        selectedUsers.slice(0, selectedIndex),
        selectedUsers.slice(selectedIndex + 1)
      );
    }
    setSelected(newSelected);
    setSelectedUsers(newSelectedUsers);
  };
  return (
    <Page title="Profile Settings" userInfo={userInfo}>
      <Container maxWidth="xl">
        {userInfo ? <UsersListCall /> : null}
        <Typography variant="h2" sx={{ mb: 5 }}>
          User Settings
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={8}>
            {editting ? (
              <FormikProvider value={formik}>
                <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
                  <Stack direction="column">
                    <h3>Name:</h3>
                    <TextField
                      fullWidth
                      type="text"
                      {...getFieldProps('firstName')}
                      error={Boolean(touched.firstName && errors.firstName)}
                      helperText={touched.firstName && errors.firstName}
                    />
                    <TextField
                      fullWidth
                      type="text"
                      {...getFieldProps('lastName')}
                      error={Boolean(touched.lastName && errors.lastName)}
                      helperText={touched.lastName && errors.lastName}
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
                    <h3>Phone:</h3>
                    <TextField
                      fullWidth
                      type="phone"
                      {...getFieldProps('phone')}
                      error={Boolean(touched.phone && errors.phone)}
                      helperText={touched.phone && errors.phone}
                    />
                    <br />
                    <br />
                    <Button
                      fullWidth
                      size="large"
                      type="submit"
                      variant="contained"
                      // loading={registerLoading ? isSubmitting : null}
                    >
                      Save Changes
                    </Button>
                  </Stack>
                </Form>
              </FormikProvider>
            ) : (
              <Stack direction="column">
                <h3>Name:</h3>
                <p>
                  {userInfo && userInfo.first_name} {userInfo && userInfo.last_name}
                </p>
                <br />
                <h3>Email:</h3>
                <p>{userInfo && userInfo.email ? userInfo.email : 'None'}</p>
                <br />
                <h3>Phone Number:</h3>
                <p>{userInfo && userInfo.phone ? userInfo.phone : 'None'}</p>
                <br />
                <Button fullWidth size="large" variant="contained" onClick={() => setEditting(true)}>
                  Edit
                </Button>
              </Stack>
            )}
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            {' '}
          </Grid>
        </Grid>
        <Card sx={{ marginTop: '3%', marginBottom: '3%', padding: '3%' }}>
          <UserListToolbar
            numSelected={selected.length}
            filterName={filterName}
            onFilterName={handleFilterByName}
            selectedUsers={selectedUsers}
            setSelected
            setSelectedUsers
          />
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
                    const { id, first_name, last_name, email, status, is_enterprise_owner } = row;
                    const isItemSelected = selected.indexOf(id) !== -1;
                    if (email !== 'reid@gmail.com' && email !== 'reidelkins3@gmail.com') {
                      return (
                        <TableRow hover key={id} tabIndex={-1}>
                          {userInfo && userInfo.status === 'admin' ? (
                            is_enterprise_owner ? (
                              <div />
                            ) : (
                              <TableCell padding="checkbox">
                                <Checkbox checked={isItemSelected} onChange={(event) => handleClick(event, id)} />
                              </TableCell>
                            )
                          ) : null}

                          <TableCell component="th" scope="row" padding="none">
                            <Stack direction="row" alignItems="center" spacing={2}>
                              <Typography variant="subtitle2" noWrap>
                                {first_name} {last_name}
                              </Typography>
                            </Stack>
                          </TableCell>
                          <TableCell align="left">{email}</TableCell>
                          <TableCell align="left">{is_enterprise_owner ? 'Enterprise Admin' : status}</TableCell>
                          <TableCell align="left">
                            {(() => {
                              if (status === 'pending' && userInfo && userInfo.status === 'admin') {
                                return (
                                  <Button
                                    aria-label="Send Reminder"
                                    component="label"
                                    onClick={(event) => sendReminder(event, email)}
                                  >
                                    &nbsp;&nbsp;&nbsp;Send Reminder
                                  </Button>
                                );
                              }
                              if (status === 'active' && userInfo && userInfo.status === 'admin') {
                                return (
                                  <Button
                                    aria-label="Make Admin"
                                    component="label"
                                    onClick={(event) => makeAdmin(event, id)}
                                  >
                                    &nbsp;&nbsp;&nbsp;Make Admin
                                  </Button>
                                );
                              }
                              return null;
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
        {userInfo && userInfo.status === 'admin' && (
          <>
            <NewUserModal />
            <br />
            {userInfo.company.product.id === 'price_1MhxfPAkLES5P4qQbu8O45xy' ? (
              <UpgradeFromFree />
            ) : (
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
            )}
          </>
        )}

        <Box>
          <Typography variant="h3" sx={{ mt: 5 }}>
            Mobile App Authentication (2FA)
          </Typography>
          <p style={{ marginBottom: 20 }}>Secure your account with TOTP two-factor authentication.</p>
          {userInfo && <TwoFactorAuth userInfo={userInfo} />}
        </Box>

        <Box>
          <Typography variant="h3" sx={{ mt: 5 }}>
            CRM Integration
          </Typography>
          <p style={{ marginBottom: 20 }}>
            Connect IMCM With Your CRM! If you don't see your CRM listed, suggest it to us!
          </p>
          <CRMIntegrationModal user={userInfo} />
        </Box>
      </Container>
    </Page>
  );
}
