export const handleChangePage = (event, newPage, setPage) => {
    // fetch new page if two away from needing to see new page
    // if (((newPage + 2) * rowsPerPage) % 1000 === 0) {
    //   dispatch(clientsAsync(((newPage + 2) * rowsPerPage) / 1000 + 1));
    // }
    
    setPage(newPage);
};

export const handleChangeRowsPerPage = (event, setRowsPerPage, setPage) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
};

export const handleRequestSort = (event, property, orderBy, order, setOrder, setOrderBy) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
};
