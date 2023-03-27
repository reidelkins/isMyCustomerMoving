import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {useDispatch } from 'react-redux';
// material
import { styled } from '@mui/material/styles';
import { Toolbar, Tooltip, IconButton, Typography, OutlinedInput, InputAdornment } from '@mui/material';
import { useAuth0 } from "@auth0/auth0-react";
// component
import Iconify from '../../../components/Iconify';
import CustomerDataFilter  from './CustomerDataFilter';
// redux
import { deleteClientAsync } from '../../../redux/actions/usersActions';

// ----------------------------------------------------------------------

const RootStyle = styled(Toolbar)(({ theme }) => ({
  height: 96,
  display: 'flex',
  justifyContent: 'space-between',
  padding: theme.spacing(0, 1, 0, 3),
}));

const SearchStyle = styled(OutlinedInput)(({ theme }) => ({
  width: 240,
  transition: theme.transitions.create(['box-shadow', 'width'], {
    easing: theme.transitions.easing.easeInOut,
    duration: theme.transitions.duration.shorter,
  }),
  '&.Mui-focused': { width: 320, boxShadow: theme.customShadows.z8 },
  '& fieldset': {
    borderWidth: `1px !important`,
    borderColor: `${theme.palette.grey[500_32]} !important`,
  },
}));

// ----------------------------------------------------------------------

ClientListToolbar.propTypes = {
  numSelected: PropTypes.number,
  filterName: PropTypes.string,
  onFilterName: PropTypes.func,
  selectedClients: PropTypes.array,
  product: PropTypes.string
};

export default function ClientListToolbar({ numSelected, filterName, onFilterName, selectedClients, product }) {
  const dispatch = useDispatch();
  const { getAccessTokenSilently } = useAuth0();
  const [accessToken, setAccessToken] = useState(null);

  useEffect(() => {
    const fetchAccessToken = async () => {
      const token = await getAccessTokenSilently();
      setAccessToken(token);
    };

    fetchAccessToken();

    // return a cleanup function to cancel any pending async operation and prevent updating the state on an unmounted component
    return () => {
      setAccessToken(null);
    };
  }, [getAccessTokenSilently]);


  const clickDelete = (event, clients) => {
    dispatch(deleteClientAsync(clients, accessToken));
    const timer = Math.ceil(clients.length / 1000)*250;
    setTimeout(() => {
     window.location.reload();
    }, timer);

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
      {numSelected > 0 ? (
        <Typography component="div" variant="subtitle1">
          {numSelected} selected
        </Typography>
      ) : (
        <SearchStyle
          value={filterName}
          onChange={onFilterName}
          placeholder="Search user..."
          startAdornment={
            <InputAdornment position="start">
              <Iconify icon="eva:search-fill" sx={{ color: 'text.disabled', width: 20, height: 20 }} />
            </InputAdornment>
          }
        />
      )}

      {numSelected > 0 ? (
        <Tooltip title="Delete">
          <IconButton onClick={(event)=>clickDelete(event, selectedClients)}>
            <Iconify icon="eva:trash-2-fill" />
          </IconButton>
        </Tooltip>
      ) : (
        <CustomerDataFilter product={product}/>
      )}
    </RootStyle>
  );
}
