/* eslint-disable no-nested-ternary */
/* eslint-disable no-else-return */
/* eslint-disable no-lonely-if */
import React from 'react';
import PropTypes from 'prop-types';
import { Grid, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';

import { makeDate } from '../utils/makeDate';

ClientDetailsTable.propTypes = {
  price: PropTypes.number,
  yearBuilt: PropTypes.number,
  housingType: PropTypes.string,
  equipmentInstalledDate: PropTypes.string,
};

function ClientDetailsTable({ price, yearBuilt, housingType, equipmentInstalledDate }) {
  return (
    <TableRow>
      <TableCell>
        <Grid container>
          <Grid item xs={12}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Price</TableCell>
                  <TableCell>Year Built</TableCell>
                  <TableCell>Housing Type</TableCell>
                  <TableCell style={{ width: '25%' }}>Installation Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>{price && price > 0 ? price.toLocaleString() : 'N/A'}</TableCell>
                  <TableCell>{yearBuilt !== 0 ? yearBuilt : 'N/A'}</TableCell>
                  <TableCell>
                    {housingType && housingType !== ' '
                      ? housingType
                          .replace(/_/g, ' ')
                          .split(' ')
                          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                          .join(' ')
                      : 'N/A'}
                  </TableCell>
                  <TableCell>{equipmentInstalledDate ? makeDate(equipmentInstalledDate) : 'N/A'}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </Grid>
        </Grid>
      </TableCell>
    </TableRow>
  );
}

export default ClientDetailsTable;
