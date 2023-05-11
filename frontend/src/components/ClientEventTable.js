/* eslint-disable no-nested-ternary */
/* eslint-disable no-else-return */
/* eslint-disable no-lonely-if */
import React from 'react';
import PropTypes from 'prop-types';
import {
    Grid,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    Typography,
} from '@mui/material';

import SearchNotFound from './SearchNotFound';
import { makeDate } from '../utils/makeDate';

const RowInformation = (info) => {
    if (!info) return null;
    
    
    const update = info.info;
    if (update.listed) {
        if (update.status === 'House For Sale') {
            return (
                <Typography>
                    Home listed for sale on {makeDate(update.listed)}
                </Typography>
            )
        } else if (update.status === 'Taken Off Market') {
            return (
                <Typography>
                    Home taken off market on {makeDate(update.date)}
                </Typography>
            )
        } else {
            return (
                <Typography>
                    Home sold on {update.listed}
                </Typography>
            )
        }
    } else {
        if (update.note) {
            return (
                <Typography>
                    Note changed to "{update.note}"
                </Typography>
            )
        } else if (update.error_flag !== null) {
            if (update.error_flag) {
                return (
                    <Typography>
                        Client housing status was marked as incorrect
                    </Typography>
                )
            } else {
                return (
                    <Typography>
                        Error flag was manually removed
                    </Typography>
                )
            }
        } else {
            return (
                <Typography>
                    Client was marked as {update.contacted ? 'contacted' : 'not contacted'}
                </Typography>
            )
        }
    }

}

ClientEventTable.propTypes = {
    clientUpdates: PropTypes.array.isRequired,
};

function ClientEventTable ({clientUpdates}) {
    return (
        <TableRow>
        <TableCell>
            <Grid container>
            <Grid item xs={12}>
                <Table size='small'  >
                <TableHead>
                    <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell >Event Description</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {clientUpdates.length > 0 ? clientUpdates.map((update, index) => (                      
                    <TableRow key={index}>
                        <TableCell>{makeDate(update.date)}</TableCell>
                        <TableCell>
                            <RowInformation info={update}/>                        
                        </TableCell>
                    </TableRow>
                    )) : (
                        <TableRow>
                        <TableCell align="center" colSpan={6} sx={{ py: 3 }}>
                            <SearchNotFound searchQuery="" tipe="event" />
                        </TableCell>
                        </TableRow>
                    )
                    }
                </TableBody>
                </Table>
            </Grid>
            </Grid>
        </TableCell>
        </TableRow>
    )
}

export default ClientEventTable;
