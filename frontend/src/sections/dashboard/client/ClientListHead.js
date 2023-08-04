import React from 'react';
import PropTypes from 'prop-types';
import { TableCell, TableSortLabel, Box } from '@mui/material';

const ClientListHead = ({ order, orderBy, headLabel, onRequestSort }) => {
  const createSortHandler = (property) => (event) => {
    onRequestSort(event, property);
  };

  return (
    <TableHead>
      <TableRow>
        {headLabel.map((headCell) => (
          <TableCell
            key={headCell.id}
            align={headCell.alignRight ? 'right' : 'left'}
            sortDirection={orderBy === headCell.id ? order : false}
          >
            <TableSortLabel
              active={orderBy === headCell.id}
              direction={orderBy === headCell.id ? order : 'asc'}
              onClick={createSortHandler(headCell.id)}
            >
              {headCell.label}
              {orderBy === headCell.id ? (
                <Box sx={{ ...visuallyHidden }}>
                  {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                </Box>
              ) : null}
            </TableSortLabel>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
};

ClientListHead.propTypes = {
  order: PropTypes.oneOf(['asc', 'desc']),
  orderBy: PropTypes.string,
  headLabel: PropTypes.array,
  onRequestSort: PropTypes.func,
};

export default ClientListHead;