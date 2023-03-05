import PropTypes from 'prop-types';
import {useDispatch } from 'react-redux';
// material
import { styled } from '@mui/material/styles';
import { Toolbar, Tooltip, IconButton, Typography, OutlinedInput } from '@mui/material';
// component
import Iconify from '../../../components/Iconify';
// redux
import { deleteUserAsync } from '../../../redux/actions/usersActions';

// ----------------------------------------------------------------------

const RootStyle = styled(Toolbar)(({ theme }) => ({
  height: 24,
  display: 'flex',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1, 0, 3),
}));

// ----------------------------------------------------------------------

UserListToolbar.propTypes = {
  numSelected: PropTypes.number,
  selectedUsers: PropTypes.array,
};

export default function UserListToolbar({ numSelected, selectedUsers }) {
  const dispatch = useDispatch();

  const clickDelete = (event, Users) => {
    dispatch(deleteUserAsync(Users));
    setTimeout(() => {
    window.location.reload();
    }, 200);

  };

  return (
    <RootStyle
      sx={{
        ...(numSelected > 0 && {
          color: 'primary.main',
          bgcolor: 'primary.lighter',
        }),
      }}
    >
      {numSelected > 0 && (
        <Typography component="div" variant="subtitle1">
          {numSelected} selected
        </Typography>
      ) }

      {numSelected > 0 && (
        <Tooltip title="Delete">
          <IconButton onClick={(event)=>clickDelete(event, selectedUsers)}>
            <Iconify icon="eva:trash-2-fill" />
          </IconButton>
        </Tooltip>
      ) }
    </RootStyle>
  );
}
