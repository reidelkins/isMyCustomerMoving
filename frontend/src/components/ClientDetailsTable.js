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

const RowInformation = (info) => {
    if (!info) return null;
    
    const update = info.info;
    if (update.listed) {
        if (update.status === 'House For Sale') {
            return (
                <Typography>
                    Home listed for sale on {update.listed}
                </Typography>
            )
        } else if (update.status === 'Taken Off Market') {
            return (
                <Typography>
                    Home taken off market on {update.date}
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
        } else {
            return (
                <Typography>
                    Client was marked as {update.contacted ? 'contacted' : 'not contacted'}
                </Typography>
            )
        }
    }

}

ClientDetailsTable.propTypes = {
    price: PropTypes.number,
    yearBuilt: PropTypes.number,
    housingType: PropTypes.string,
};

function ClientDetailsTable ({price, yearBuilt, housingType}) {
    return (
        <TableRow>
        <TableCell>
            <Grid container>
            <Grid item xs={12}>
                <Table size='small'  >
                <TableHead>
                    <TableRow>
                    <TableCell>Price</TableCell>
                    <TableCell >Year Built</TableCell>
                    <TableCell >Housing Type</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    <TableRow>
                        <TableCell>{price && price > 0 ? price.toLocaleString() : "N/A"}</TableCell>
                        <TableCell>{yearBuilt !== 0 ? yearBuilt : "N/A"}</TableCell>
                        <TableCell>{housingType && housingType !== " " ? housingType.replace(/_/g, ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '): "N/A"}</TableCell>
                    </TableRow>
                </TableBody>
                </Table>
            </Grid>
            </Grid>
        </TableCell>
        </TableRow>
    )
}

export default ClientDetailsTable;
