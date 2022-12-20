import {useState} from 'react';
import { useSelector } from 'react-redux';
import * as Yup from 'yup';
import { useFormik } from 'formik';

import { TextField, Card, Grid, Container, Typography, Stack, Button, TableContainer, Table, TableBody, TableCell, TableRow } from '@mui/material';

// components
import Page from '../components/Page';
import Scrollbar from '../components/Scrollbar';
import { UserListHead } from '../sections/@dashboard/user';
import NewUserModal from '../components/NewUserModal';
import IntegrateSTModal from '../components/IntegrateSTModal';
import AddSecretModal from '../components/AddSecretModal';
import ResetPasswordModal from '../components/ResetPasswordModal';

import { showLoginInfo } from '../redux/actions/authActions';


// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'employee', label: 'Name', alignRight: false },
  { id: 'email', label: 'Email', alignRight: false },
  { id: 'role', label: 'Role', alignRight: false },
  { id: 'status', label: 'Status', alignRight: false },
];

export default function ProfileSettings() {
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;
  const [editting, setEditting] = useState(false);

  const SettingsSchema = Yup.object().shape({
    name: Yup.string().required('Name is required'),
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
    servTitan: Yup.string(),
  });

  const formik = useFormik({
    initialValues: {
      name: userInfo.name,
      email: userInfo.id,
      servTitan: userInfo.company.tenantID,
    },
    validationSchema: SettingsSchema,
    onSubmit: () => {
      console.log(values.servTitan)
    },
  });

  const { errors, touched, values, getFieldProps } = formik;

  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('status');

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
    console.log(userInfo);
  };

  const save = () => {
    setEditting(false);  
  };
  return (
    <Page title="Profile Settings">
      <Container maxWidth="xl">
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
                  <TextField
                    fullWidth
                    type="text"  
                    {...getFieldProps('servTitan')}
                    error={Boolean(touched.servTitan && errors.servTitan)}
                    helperText={touched.servTitan && errors.servTitan}
                  />
                  <br />
                  <Button variant="contained" onClick={save} >Save</Button>             
                </Stack>
              ):(
                <Stack direction='column'>
                  <h3>Name:</h3>
                  <p>{userInfo.name}</p>
                  <br />
                  <h3>Email:</h3>
                  <p>{userInfo.id}</p>
                  <br />
                  <h3>Service Titan Tenant ID:</h3>                  
                  {userInfo.company.tenantID ? <p>{userInfo.company.tenantID}</p> : <IntegrateSTModal userInfo={userInfo} />}
                  {(!userInfo.company.clientID && userInfo.company.tenantID) && <AddSecretModal />}
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
          <Scrollbar>
            <TableContainer sx={{ minWidth: 800 }}>
              <Table>
                <UserListHead
                  headLabel={TABLE_HEAD}
                  checkbox={0}
                  order={order}
                  orderBy={orderBy}
                  rowCount={0}
                  numSelected={0}
                  onRequestSort={handleRequestSort}                  
                />
                <TableBody>
                  <TableRow
                    hover
                    // key={id}
                    tabIndex={-1}
                  >                    
                    <TableCell component="th" scope="row" padding="none">
                      <Stack direction="row" alignItems="center" spacing={2}>
                        <Typography variant="subtitle2" noWrap>
                          Here is the name
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell align="left">EMAIL</TableCell>
                    <TableCell align="left">Role</TableCell>
                    <TableCell align="left">Status</TableCell>                    
                  </TableRow>
                </TableBody>                
              </Table>
            </TableContainer>
          </Scrollbar>
        </Card>
        <ResetPasswordModal />
        <NewUserModal />
                    
      </Container>
    </Page>
  );
}
