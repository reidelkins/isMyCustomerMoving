import React, { useState, useEffect } from 'react';
import {
    Box,    
    Card,
    LinearProgress,
    Stack,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableRow,
    TablePagination,
    Tooltip
} from '@mui/material';
import PropTypes from 'prop-types';
import { useSelector } from 'react-redux';

import Scrollbar from './Scrollbar';
import { ClientListHead } from '../sections/@dashboard/client';
import { handleChangePage, handleChangeRowsPerPage, handleRequestSort } from '../utils/dataTableFunctions';
import { applySortFilter, getComparator } from '../utils/filterFunctions';
import { selectClients } from '../redux/actions/usersActions';
import NewAddressListCall from '../redux/calls/NewAddressListCall';

const TABLE_HEAD = [
  { id: 'name', label: 'Name', alignRight: false },
  { id: 'address', label: 'Old Address', alignRight: false },
  { id: 'newAddress', label: 'New Address', alignRight: false },
  { id: 'newCity', label: 'New City', alignRight: false },
  { id: 'newState', label: 'New State', alignRight: false },
//   { id: 'newZipCode', label: 'New Zip Code', alignRight: false }
];

NewAddressData.propTypes = {
    userInfo: PropTypes.object
};

export default function NewAddressData({ userInfo }) {    
    const listClient = useSelector(selectClients);
    const { NEWADDRESSLIST, loading } = listClient;

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);    
    const [shownClients, setShownClients] = useState(0);
    const [filteredClients, setFilteredClients] = useState([]);
    const [clientListLength, setClientListLength] = useState(0);
    useEffect(() => {
        if (NEWADDRESSLIST.length < clientListLength) {
        setPage(0);
        setShownClients(0);
        }
        setClientListLength(NEWADDRESSLIST.length);
    }, [NEWADDRESSLIST, clientListLength, NEWADDRESSLIST.length]);
    useEffect(() => {
        if (filteredClients.length < NEWADDRESSLIST.length) {
            console.log("setting shown clients")
            setShownClients(filteredClients.length);
        } else {
            setShownClients(NEWADDRESSLIST.length);
        }
    }, [filteredClients, NEWADDRESSLIST.length]);
    const [orderBy, setOrderBy] = useState('status');
    const [order, setOrder] = useState('asc');
    
    // const [filterName, setFilterName] = useState('');
    const filterName = '';
    useEffect(() => {
        if (NEWADDRESSLIST.length > 0) {
            console.log("filtering clients")
            setFilteredClients(applySortFilter(NEWADDRESSLIST, getComparator(order, orderBy), filterName, userInfo.status));
        } else {
        setFilteredClients([]);
        }
    }, [NEWADDRESSLIST, order, orderBy, filterName, userInfo]);

    
    return (
        <Card sx={{ marginBottom: '3%' }}>
            {userInfo ? <NewAddressListCall /> : null}
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
                        onRequestSort={(event, property) => handleRequestSort(event, property, orderBy, order, setOrder, setOrderBy)}
                    />
                    <TableBody>
                        {filteredClients
                                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                    .map((row) => {
                                    const {
                                        id,
                                        name,
                                        address,
                                        city,
                                        state,
                                        // zip_code: zipCode,
                                        new_address: newAddress,
                                        new_city: newCity,
                                        new_state: newState,
                                        // new_zip_code: newZipCode,
                                    } = row;
                                    
                                    if (newAddress !== null) {
                                        return (
                                            <React.Fragment key={row.id}>
                                                <Tooltip title="Click For Expanded Details">
                                                    <TableRow
                                                    hover
                                                    key={id}
                                                    tabIndex={-1}                                                
                                                    
                                                    >                                                                                                
                                                    <TableCell component="th" scope="row" padding='3%'>
                                                        <Stack direction="row" alignItems="center" spacing={2}>
                                                        <Typography variant="subtitle2" noWrap>
                                                            {name}
                                                        </Typography>
                                                        </Stack>
                                                    </TableCell>
                                                    <TableCell align="left">{address}, {city}, {state}</TableCell>
                                                    <TableCell align="left">{newAddress}</TableCell>
                                                    <TableCell align="left">{newCity}</TableCell>
                                                    <TableCell align="left">{newState}</TableCell>
                                                    {/* <TableCell align="left">{newZipCode}</TableCell>                                                 */}
                                                    </TableRow>
                                                </Tooltip>
                                            
                                            </React.Fragment>
                                        );
                                    }
                                    return (
                                        null
                                    );
                                    })}
                    </TableBody>
                </Table>
                </TableContainer>
            </Scrollbar>

            <TablePagination
                rowsPerPageOptions={[10, 50, 100]}
                component="div"
                count={shownClients}
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
    )
}