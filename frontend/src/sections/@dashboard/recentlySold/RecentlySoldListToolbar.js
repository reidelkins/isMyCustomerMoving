// material
import { styled } from '@mui/material/styles';
import { Toolbar } from '@mui/material';
// component
import RecentlySoldDataFilter from './RecentlySoldDataFilter';
// redux

// ----------------------------------------------------------------------

const RootStyle = styled(Toolbar)(({ theme }) => ({
  height: 96,
  display: 'flex',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1, 0, 3),
}));


// ----------------------------------------------------------------------
export default function RecentlySoldListToolbar() {

  return (
    <RootStyle>      
        <RecentlySoldDataFilter />
    </RootStyle>
  );
}
