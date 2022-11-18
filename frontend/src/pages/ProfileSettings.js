import {useState} from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { Card, Grid, Container, Typography, Stack, Button, TableContainer, Table, TableBody, TableCell, TableRow } from '@mui/material';

// components
import Page from '../components/Page';
import Scrollbar from '../components/Scrollbar';
import { UserListHead } from '../sections/@dashboard/user';
import NewUserModal from '../components/NewUserModal';


// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'employee', label: 'Name', alignRight: false },
  { id: 'employee', label: 'Email', alignRight: false },
  { id: 'role', label: 'Role', alignRight: false },
  { id: 'status', label: 'Status', alignRight: false },
];


export default function ProfileSettings() {
  const userLogin = useSelector((state) => state.userLogin);
  const { userInfo } = userLogin;

  // const listWorker = useSelector((state) => state.listWorker);
  // const { loading, error, WORKERLIST } = listWorker;

  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('status');

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const addUser = () => {
    // dispatch(update());
  };

  return (
    <Page title="Profile Settings">
      <Container maxWidth="xl">
        <Typography variant="h2" sx={{ mb: 5 }}>
          User Settings
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={8}>
            <Stack direction='column'>
              <h3>Name:</h3>
              <p>{userInfo.name}</p>
              <br />
              <h3>Email:</h3>
              <p>{userInfo.email}</p>
              <br />
              <Button variant="contained">Reset Password</Button>  
            </Stack>
            
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <h2>Test 2</h2>
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
                  onSelectAllClick={console.log("sup")}
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

                {/* {isUserNotFound && (
                  <TableBody>
                    <TableRow>
                      <TableCell align="center" colSpan={6} sx={{ py: 3 }}>
                        <SearchNotFound searchQuery={filterName} />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                )} */}
              </Table>
            </TableContainer>
          </Scrollbar>
        </Card>
        <NewUserModal/>
        

        
      </Container>
    </Page>
  );
}
