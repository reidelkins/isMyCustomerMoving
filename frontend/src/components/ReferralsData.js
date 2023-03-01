import React, { useEffect, useState } from 'react';
import {Card, Table, TableBody, TableCell, TableContainer, TableRow, Typography, Stack, IconButton} from '@mui/material';

import Scrollbar from './Scrollbar';
import Iconify from './Iconify';
import { ReferralListHead } from '../sections/@dashboard/referral';


const ReferralsData = ({refs, company, incoming}) => {
    const emptyRows = 0;
    const [referrals, setReferrals] = useState([]);
    useEffect(() => {
        if (refs.results) {
          if (incoming) {
            setReferrals(refs.results.filter(referral => referral.referredTo.id === company));
          } else {
            setReferrals(refs.results.filter(referral => referral.referredFrom.id === company));
          }
        }
    }, [refs, incoming])

  const updateContacted = (event, id, contacted) => {
    console.log("updateContacted", id, contacted)  
  };

  const toOrFrom = incoming ? "Referral From" : "Referral To";
  const TABLE_HEAD = [
    { id: 'name', label: 'Name', alignRight: false },
    { id: 'phone', label: 'Phone', alignRight: false },
    { id: 'referral', label: toOrFrom, alignRight: false },
    { id: 'contacted', label: 'Contacted', alignRight: false },
  ];
    return (
        <div>
        <h1>Referrals {incoming ? "Incoming" : "Outgoing"}</h1>
        <Card sx={{marginTop:"3%", marginBottom:"3%", padding:'3%'}}>
          {/* {loading ? (
            <Box sx={{ width: '100%' }}>
              <LinearProgress />
            </Box>
          ) : null} */}
          <Scrollbar>
            <TableContainer sx={{ minWidth: 800 }}>
              <Table>
                <ReferralListHead
                  headLabel={TABLE_HEAD}                
                />
                <TableBody>
                  {referrals.map((row) => {
                    const { client, referredFrom, referredTo, id } = row;
                    const { name, phoneNumber } = client;
                    const { name: referredFromName } = referredFrom;
                    const { name: referredToName } = referredTo;
                    const contacted = false;
                    return (
                        <TableRow
                          hover
                          key={id}
                          tabIndex={-1}>                          
                                          
                          <TableCell component="th" scope="row" padding="none">
                            <Stack direction="row" alignItems="center" spacing={2}>
                              <Typography variant="subtitle2" noWrap>
                                {name}
                              </Typography>
                            </Stack>
                          </TableCell>
                          <TableCell align="left">{phoneNumber}</TableCell>
                          <TableCell align="left">
                            {incoming ? referredFromName : referredToName}
                          </TableCell>
                          <TableCell>
                            {(() => {
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
                              
                            })()}                          
                          </TableCell>
                          
                        </TableRow>
                      )                
                  })}                
                  {emptyRows > 0 && (
                    <TableRow style={{ height: 53 * emptyRows }}>
                      <TableCell colSpan={2} />
                    </TableRow>
                  )}
                </TableBody>                
              </Table>
            </TableContainer>
          </Scrollbar>
        </Card>
        </div>
    );
}

export default ReferralsData;
