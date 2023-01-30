/* eslint-disable camelcase */
import _, { filter} from 'lodash';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// material
import {
  Box,
  Card,
  Table,
  Stack,
  LinearProgress,
  TableRow,
  TableBody,
  TableCell,
  Container,
  Typography,
  TableContainer,
  TablePagination,
} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';

// components
import NewCompanyModal from '../components/NewCompanyModal';
import Page from '../components/Page';
import Scrollbar from '../components/Scrollbar';
import SearchNotFound from '../components/SearchNotFound';
import { ClientListHead } from '../sections/@dashboard/client';

import RecentlySoldListCall from '../redux/calls/RecentlySoldListCall';
import { selectRecentlySold, recentlySoldAsync } from '../redux/actions/usersActions';
import { logout, showLoginInfo } from '../redux/actions/authActions';

// ----------------------------------------------------------------------

const TABLE_HEAD = [
  { id: 'sold', label: 'Date Sold', alignRight: false },
  { id: 'address', label: 'Address', alignRight: false },
  { id: 'zipCode', label: 'Zip Code', alignRight: false },

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

export function applySortFilter(array, comparator, query) {
  const stabilizedThis = array.map((el, index) => [el, index]);
  
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  if (query) {
    return filter(array, (_recentlySold) => _.some(_recentlySold, val=>val && val.toString().toLowerCase().includes(query.toLowerCase())));
  }
  return stabilizedThis.map((el) => el[0]);
}

export default function RecentlySoldData() {
  const dispatch = useDispatch();
  const navigate = useNavigate();  

  const userLogin = useSelector(showLoginInfo);
  const { userInfo, twoFA } = userLogin;
  useEffect(() => {
    if (!userInfo) {
      dispatch(logout());
      navigate('/login', { replace: true });
      window.location.reload(false);
    } else if (userInfo.otp_enabled && twoFA === false) {
      navigate('/login', { replace: true });
    }

  }, [userInfo, dispatch, navigate]);

  const listRecentlySold = useSelector(selectRecentlySold);
  const {loading, RECENTLYSOLDLIST, error } = listRecentlySold;

  const [page, setPage] = useState(0);
  
  const [order, setOrder] = useState('asc');

  const [orderBy, setOrderBy] = useState('listed');

  const [filterName, setFilterName] = useState('');

  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [shownClients, setShownClients] = useState(0);

  const [csvLoading, setCsvLoading] = useState(false);

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (event, newPage) => {
    // fetch new page if two away from needing to see new page
    if ((newPage+2) * rowsPerPage % 1000 === 0) {
      dispatch(recentlySoldAsync(((newPage+2) * rowsPerPage / 1000)+1))
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

  // const exportCSV = async () => {
  //   if (RECENTLYSOLDLIST.length === 0) { return }
  //   const config = {
  //     headers: {
  //       'Content-type': 'application/json',
  //       Authorization: `Bearer ${userInfo.access}`,
  //     },
  //   };
  //   setCsvLoading(true);
  //   const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/allClients/${userInfo.id}`, config);
  //   let csvContent = 'data:text/csv;charset=utf-8,';
  //   csvContent += 'Name,Address,City,State,ZipCode,Status,Contacted,Note,Phone Number\r\n';
  //   data.forEach((n) => {
  //     csvContent += `${n.name}, ${n.address}, ${n.city}, ${n.state}, ${n.zipCode}, ${n.status}, ${n.contacted}, ${n.note}, ${n.phoneNumber}\r\n`
  //   });

  //   const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  //   // Create a download link for the CSV file
  //   const link = document.createElement('a');
  //   link.href = window.URL.createObjectURL(blob);
  //   const d1 = new Date().toLocaleDateString('en-US')
  //   const docName = `isMyCustomerMoving_${d1}`    

  //   link.setAttribute('download', `${docName}.csv`);
  //   document.body.appendChild(link); // add the link to body
  //   link.click();
  //   document.body.removeChild(link); // remove the link from body
  //   setCsvLoading(false);
  // };

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - RECENTLYSOLDLIST.length) : 0;
  const filteredRecentlySold = userInfo ? applySortFilter(RECENTLYSOLDLIST, getComparator(order, orderBy), filterName) : [];
  // TODO, add val here to set length too
  useEffect(() => {
    setShownClients(0)
  }, [])

  return (
    <Page title="User">
      <Container>
        {userInfo ? <RecentlySoldListCall /> : null}
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
            {/* <Stack direction="row" alignItems="center" justifyContent="space-around" mb={5} mx={10}>
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
            </Stack> */}
            <Card sx={{marginBottom:"3%"}}>
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
                      numSelected={0}
                      onRequestSort={handleRequestSort}
                      onSelectAllClick={handleRequestSort}
                      checkbox={0}
                    />
                    <TableBody>
                      {filteredRecentlySold.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                        const { id, address, zipCode, listed} = row;
                        
                        return (
                          <React.Fragment key={row.id}>
                            <TableRow
                              hover
                              key={id}
                              tabIndex={-1}
                              role="checkbox"
                            >
                              <TableCell component="th" scope="row" padding="none">
                                <Stack direction="row" alignItems="center" spacing={2}>
                                  <Typography variant="subtitle2" noWrap>
                                    {listed}
                                  </Typography>
                                </Stack>
                              </TableCell>
                              <TableCell align="left">{address}</TableCell>
                              <TableCell align="left">{zipCode}</TableCell>                                                    
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
          </>
        )}
      </Container>
    </Page>
  );
}
