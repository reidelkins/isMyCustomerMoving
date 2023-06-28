import _, { filter} from 'lodash';

// ----------------------------------------------------------------------
// change this to sort by status
export function descendingComparator(a, b, orderBy) {
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

export function applySortFilter(array, comparator, query, userInfo) {
  let stabilizedThis = array;
  if (userInfo === 'admin') {
    stabilizedThis = array.map((el, index) => [el, index]);
  } else {
    stabilizedThis = array.filter((el) => el.status !== 'No Change').map((el, index) => [el, index]);
  }
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  if (query) {
    return filter(array, (_user) =>
      _.some(_user, (val) => val && val.toString().toLowerCase().includes(query.toLowerCase()))
    );
  }
  return stabilizedThis.map((el) => el[0]);
}
