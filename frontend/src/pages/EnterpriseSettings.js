import {useEffect, useState} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { Box, Checkbox, LinearProgress, Link, TextField, Card, Grid, Container, Typography, Stack, Button, TableContainer, Table, TableHead, TableBody, TableCell, TableRow } from '@mui/material';
import { showLoginInfo, logout } from '../redux/actions/authActions';
import { enterpriseInfo, switchCompany } from '../redux/actions/enterpriseActions';
import EnterpriseCall from '../redux/calls/EnterpriseListCall';
// components
import Page from '../components/Page';
import Scrollbar from '../components/Scrollbar';


export default function EnterpriseSettings() {
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
      window.location.reload(true);
    }

  }, [userInfo, dispatch, navigate]);

  const enterprise = useSelector(enterpriseInfo);
  const { name, companies, loading } = enterprise;

  const page = 0;
  const rowsPerPage = 50;

  const emptyRows = page > 0 ? Math.max(0, (1 + page) * rowsPerPage - companies.length) : 0;

  const TABLE_HEAD = [
  {id: 'selected', label: 'Selected', alignRight: false},
  { id: 'company', label: 'Name', alignRight: false },
  { id: 'email', label: 'Email', alignRight: false },
  { id: 'phone', label: 'Phone', alignRight: false },
  { id: 'accounts', label: 'Accounts', alignRight: false },
  { id: 'customers', label: 'Customers', alignRight: false},
  { id: 'leads', label: 'Leads Generated', alignRight: false },
  { id: 'revenue', label: 'Revenue (Coming Soon)', alignRight: false },
  // { id: 'status', label: 'Account Created', alignRight: false },
];
  return (
    <Page title="Enterprise Settings | IsMyCustomerMoving.com">
      <Container>
        {userInfo ? <EnterpriseCall /> : null}
        <Stack sx={{ mb: 5 }}>
          <Typography variant="h4">Enterprise Settings</Typography>
        </Stack>
        {userInfo && (
          <Stack direction="row" alignItems="center" justifyContent="center" mb={5}>
            <Typography variant="h3" gutterBottom>
              {name}
            </Typography>
          </Stack>
        )}
        <Card sx={{marginTop:"3%", marginBottom:"3%", padding:'3%'}}>          
          {loading ? (
            <Box sx={{ width: '100%' }}>
              <LinearProgress />
            </Box>
          ) : null}
          <Scrollbar>
            <TableContainer sx={{ minWidth: 800 }}>
              <Table>
                <TableHead>
                  <TableRow>                    
                    {TABLE_HEAD.map((headCell) => (
                      <TableCell
                        key={headCell.id}
                        align={headCell.alignRight ? 'right' : 'left'}
                      >
                        {headCell.label}
                      </TableCell>                                              
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {companies.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row) => {
                    const { id, name, phone, email, users_count: usersCount, leads_count: leadsCount, clients_count: customersCount} = row;
                    const isChecked = userInfo.company.name === name;
                    if (email !== 'reidelkins3@gmail.com') {
                      return (
                        <TableRow
                          hover
                          key={id}
                          tabIndex={-1}>
                          {userInfo.company.name === name ? (
                            <TableCell padding="checkbox" align="center">
                              <Checkbox checked={isChecked}/>
                            </TableCell>
                          ):(
                            <TableCell align="center">
                              <Button  aria-label="Make Active" component="label" onClick={()=>dispatch(switchCompany(id))}>
                                Make Active
                              </Button>
                            </TableCell>
                          )}                                              
                          <TableCell component="th" scope="row" padding="none">
                            <Stack direction="row" alignItems="center" spacing={2}>
                              <Typography variant="subtitle2" noWrap>
                                {name}
                              </Typography>
                            </Stack>
                          </TableCell>
                          <TableCell align="left">{email}</TableCell>
                          <TableCell align="left">
                            {phone}                         
                          </TableCell>
                          <TableCell align="left">
                            {usersCount}
                          </TableCell>
                          <TableCell align="left">
                            {customersCount}
                          </TableCell>
                          <TableCell align="left">
                            {leadsCount}
                          </TableCell>
                          <TableCell align="left">
                            (Coming Soon)
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
        </Container>
        </Page>

  )
}
