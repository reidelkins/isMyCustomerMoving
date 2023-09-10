/* eslint-disable camelcase */
import React, { useState, useEffect } from 'react';
// material
import {
  Button,
  Box,
  Card,
  Table,
  Stack,
  LinearProgress,
  TableRow,
  TableBody,
  TableCell,
  Link,
  Container,
  Typography,
  TableContainer,
  TablePagination,  
} from '@mui/material';

import { useSelector, useDispatch } from 'react-redux';

// components
import Page from '../../components/Page';
import Scrollbar from '../../components/Scrollbar';
import SearchNotFound from '../../components/SearchNotFound';
import { ClientListHead } from '../../sections/@dashboard/client';

import RealtorListCall from '../../redux/calls/RealtorListCall';
import { showLoginInfo } from '../../redux/actions/authActions';
import { selectRealtorInfo } from '../../redux/actions/usersActions';

import { makeDate } from '../../utils/makeDate';
import { handleChangePage, handleChangeRowsPerPage, handleRequestSort } from '../../utils/dataTableFunctions';
import { getComparator, applySortFilter } from '../../utils/filterFunctions';


// ----------------------------------------------------------------------

const TABLE_HEAD = [  
  { id: 'name', label: 'Realtor', alignRight: false },
  { id: 'agentPhone', label: 'Agent Phone', alignRight: false },
  { id: 'company', label: 'Company Name', alignRight: false },
  { id: 'brokeragePhone', label: 'Brokerage Phone', alignRight: false },
  { id: 'count', label: 'Listing Count', alignRight: false },
  
];


export default function RealtorData() {  
  const userLogin = useSelector(showLoginInfo);
  const { userInfo } = userLogin;

  const listRealtor = useSelector(selectRealtorInfo);
  const { loading, REALTORLIST, count } = listRealtor;

  const [page, setPage] = useState(0);

  const [order, setOrder] = useState('desc');

  const [orderBy, setOrderBy] = useState('listed');

  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [shownRealtors, setShownRealtors] = useState(0);

  const [csvLoading] = useState(false);

  const [realtorLength, setRealtorLength] = useState(0);

  useEffect(() => {
    if (REALTORLIST.length < realtorLength) {
      setPage(0);
      setShownRealtors(0);
    }
    setRealtorLength(REALTORLIST.length);
  }, [REALTORLIST, realtorLength]);


  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - REALTORLIST.length) : 0;
  const filteredRealtors = userInfo ? applySortFilter(REALTORLIST, getComparator(order, orderBy)) : [];
  // TODO, add val here to set length too
  useEffect(() => {
    setShownRealtors(count);
  }, [count]);

  return (
    <Page title="Realtors" userInfo={userInfo}>
      <Container>
        {userInfo ? <RealtorListCall /> : null}
        {userInfo && (
          <>
            <Stack direction="row" alignItems="center" justifyContent="space-between" mb={5}>
              <Typography variant="h4" gutterBottom>
                Welcome {userInfo.first_name.charAt(0).toUpperCase() + userInfo.first_name.slice(1)}{' '}
                {userInfo.last_name.charAt(0).toUpperCase() + userInfo.last_name.slice(1)} 👋
              </Typography>
            </Stack>
            <Card sx={{ marginBottom: '3%' }}>
              {loading ? (
                <Box sx={{ width: '100%' }}>
                  <LinearProgress />
                </Box>
              ) : null}
              {userInfo.company.recently_sold_purchased ? (
                <Scrollbar>                  
                  <TableContainer sx={{ minWidth: 800 }}>
                    <Table>
                      <ClientListHead
                        order={order}
                        orderBy={orderBy}
                        headLabel={TABLE_HEAD}
                        rowCount={rowsPerPage}
                        numSelected={0}
                        onRequestSort={(event, property) => handleRequestSort(event, property, orderBy, order, setOrder, setOrderBy)}
                        onSelectAllClick={handleRequestSort}
                        checkbox={0}
                      />
                      <TableBody>
                        {filteredRealtors.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                          const {
                            id,
                            name,
                            company,
                            agent_phone: agentPhone,
                            brokerage_phone: brokeragePhone,
                            email,
                            listing_count: count,
                            
                          } = row;

                          return (
                            <React.Fragment key={row.id}>
                              <TableRow hover key={id} tabIndex={-1} role="checkbox">
                                <TableCell align="left">{name}</TableCell>                                
                                <TableCell align="left">{agentPhone}</TableCell>
                                <TableCell align="left">{company}</TableCell>
                                <TableCell align="left">{brokeragePhone}</TableCell>
                                <TableCell align="left">{count}</TableCell>
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

                      {filteredRealtors.length === 0 && (
                        <TableBody>
                          <TableRow>
                            <TableCell align="center" colSpan={6} sx={{ py: 3 }}>
                              <SearchNotFound searchQuery={''} tipe="realtor" />
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      )}
                    </Table>
                  </TableContainer>
                </Scrollbar>
              ) : (
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="h5">Recently Sold Homes</Typography>
                  <Typography variant="subtitle2" gutterBottom>
                    You have not purchased this additional feature yet. You can add the option to get all recently sold
                    homes in your area by clicking the button below.
                  </Typography>
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
                </Box>
              )}
              <TablePagination
                  rowsPerPageOptions={[10, 50, 100]}
                  component="div"
                  count={shownRealtors}
                  rowsPerPage={rowsPerPage}
                  page={page}
                  onPageChange={(event, newPage) =>
                      handleChangePage(event, newPage, setPage)
                  }
                  onRowsPerPageChange={(event) =>
                      handleChangeRowsPerPage(event, setRowsPerPage, setPage)
                  }
              />
            </Card>            
            
          </>
        )}
      </Container>
    </Page>
  );
}
