import { useState } from 'react';
import * as Yup from 'yup';
import PropTypes from 'prop-types';
import { useDispatch } from 'react-redux';
// material
import { styled } from '@mui/material/styles';
import {
  Box,
  Checkbox,
  Dialog,
  DialogTitle,
  Grid,
  TextField,  
  Toolbar,
  Tooltip,
  IconButton,
  Typography,
  OutlinedInput,
  InputAdornment,
  Stack,
  Button,
  Alert,
} from '@mui/material';
import {
  List,
  Map,
  Add,
  Remove
} from '@mui/icons-material';

import { useFormik, Form, FormikProvider } from 'formik';

// component
import Iconify from '../../../components/Iconify';
import CustomerDataFilter from './CustomerDataFilter';
// redux
import { deleteClientAsync, saveClientTagAsync, addClientTagsAsync, removeClientTagsAsync } from '../../../redux/actions/usersActions';
import { capitalizeWords } from '../../../utils/capitalizeWords';


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
  clearSelectedClients: PropTypes.func,
  product: PropTypes.string,
  minPrice: PropTypes.string,
  setMinPrice: PropTypes.func,
  maxPrice: PropTypes.string,
  setMaxPrice: PropTypes.func,
  minYear: PropTypes.string,
  setMinYear: PropTypes.func,
  maxYear: PropTypes.string,
  setMaxYear: PropTypes.func,
  equipInstallDateMin: PropTypes.string,
  setEquipInstallDateMin: PropTypes.func,
  equipInstallDateMax: PropTypes.string,
  setEquipInstallDateMax: PropTypes.func,
  statusFilters: PropTypes.array,
  setStatusFilters: PropTypes.func,
  listOrMap: PropTypes.string,
  setListOrMap: PropTypes.func,
  tagFilters: PropTypes.array,
  setTagFilters: PropTypes.func,
  zipCode: PropTypes.string,
  setZipCode: PropTypes.func,
  city: PropTypes.string,
  setCity: PropTypes.func,
  state: PropTypes.string,
  setState: PropTypes.func,
  customerSinceMin: PropTypes.string,
  setCustomerSinceMin: PropTypes.func,
  customerSinceMax: PropTypes.string,
  setCustomerSinceMax: PropTypes.func,
  minRooms: PropTypes.string,
  setMinRooms: PropTypes.func,
  maxRooms: PropTypes.string,
  setMaxRooms: PropTypes.func,
  minBaths: PropTypes.string,
  setMinBaths: PropTypes.func,
  maxBaths: PropTypes.string,
  setMaxBaths: PropTypes.func,
  minSqft: PropTypes.string,
  setMinSqft: PropTypes.func,
  maxSqft: PropTypes.string,
  setMaxSqft: PropTypes.func,
  minLotSqft: PropTypes.string,
  setMinLotSqft: PropTypes.func,
  maxLotSqft: PropTypes.string,
  setMaxLotSqft: PropTypes.func,
  savedFilter: PropTypes.string,
  setSavedFilter: PropTypes.func,
  customerDataFilters: PropTypes.array,
  uspsChanged: PropTypes.bool,
  setUspsChanged: PropTypes.func,
  minRevenue: PropTypes.string,
  setMinRevenue: PropTypes.func,
  maxRevenue: PropTypes.string,
  setMaxRevenue: PropTypes.func,
  clientTagFilters: PropTypes.array,
  setClientTagFilters: PropTypes.func,
  clientTags: PropTypes.array,
};

export default function ClientListToolbar({
  numSelected,
  filterName,
  onFilterName,
  selectedClients,
  clearSelectedClients,
  product,
  minPrice,
  setMinPrice,
  maxPrice,
  setMaxPrice,
  minYear,
  setMinYear,
  maxYear,
  setMaxYear,
  equipInstallDateMin,
  setEquipInstallDateMin,
  equipInstallDateMax,
  setEquipInstallDateMax,
  statusFilters,
  setStatusFilters,
  listOrMap,
  setListOrMap,
  tagFilters,
  setTagFilters,
  zipCode,
  setZipCode,
  city,
  setCity,
  state,
  setState,
  customerSinceMin,
  setCustomerSinceMin,
  customerSinceMax,
  setCustomerSinceMax,
  minRooms,
  setMinRooms,
  maxRooms,
  setMaxRooms,
  minBaths,
  setMinBaths,
  maxBaths,
  setMaxBaths,
  minSqft,
  setMinSqft,
  maxSqft,
  setMaxSqft,
  minLotSqft,
  setMinLotSqft,
  maxLotSqft,
  setMaxLotSqft,
  savedFilter,
  setSavedFilter,
  customerDataFilters,
  uspsChanged,
  setUspsChanged,
  minRevenue,
  setMinRevenue,
  maxRevenue,
  setMaxRevenue,
  clientTagFilters,
  setClientTagFilters,
  clientTags
}) {
  const dispatch = useDispatch();
  const [showAlert, setShowAlert] = useState(false);
  const [createClientTagModalOpen, setCreateClientTagModalOpen] = useState(false);
  const [editClientTagsModalOpen ,setEditClientTagsModalOpen] = useState(false);
  const [removeClientTagsModalOpen, setRemoveClientTagsModalOpen] = useState(false);
  const [selectedClientTags ,setSelectedClientTags] = useState([]);
  const tagColors = [  '#E57373',  '#81C784',  '#64B5F6', '#FFC107', '#BA68C8'];
  
  const handleSelectedClientTagsChange = (event) => {
    const { value } = event.target;

    // Check if the value is already in the selectedClientTags array
    const index = selectedClientTags.indexOf(value);

    if (index === -1) {
      // If not in the array, add it
      setSelectedClientTags([...selectedClientTags, value]);
    } else {
      // If already in the array, remove it
      const updatedTags = [...selectedClientTags];
      updatedTags.splice(index, 1);
      setSelectedClientTags(updatedTags);
    }
  };

  const closeClientTagModal = () => {
    setEditClientTagsModalOpen(false);
    setRemoveClientTagsModalOpen(false);
    setSelectedClientTags([]);
  };

  const addClientsToTagGroup = () => {
    dispatch(addClientTagsAsync(selectedClientTags, selectedClients));    
    closeClientTagModal();
    clearSelectedClients();
    window.location.reload();
  };

  const removeTagsFromClients = () => {
    dispatch(removeClientTagsAsync(selectedClientTags, selectedClients));    
    closeClientTagModal();
    clearSelectedClients();
    window.location.reload();
  };

  const clickDelete = (event, clients) => {
    dispatch(deleteClientAsync(clients));
    const timer = Math.ceil(clients.length / 1000) * 250;
    setTimeout(() => {
      window.location.reload();
    }, timer);
  };

  const handleClickList = () => {
    setListOrMap('list');
  };

  const handleClickMap = () => {
    if (product === 'price_1MhxfPAkLES5P4qQbu8O45xy') {
      setShowAlert(true);
    } else {
      setListOrMap('map');
    }
  };

  const NewClientTag = Yup.object().shape({
    clientTag: Yup.string().required('Client Tag is required'),
  });

  const formik = useFormik({
    initialValues: {
      clientTag: '',
    },    
    validationSchema: NewClientTag,
    onSubmit: () => {
      dispatch(saveClientTagAsync(values.clientTag));      
      values.clientTag = '';
      setCreateClientTagModalOpen(false);

    },
  });
  const { errors, touched, values, handleSubmit, getFieldProps } = formik;
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
        <Stack direction="row" alignItems="center" spacing={1}>
          <Button 
            startIcon={<List />}
            onClick={handleClickList} 
            variant={listOrMap === 'list' ? 'contained' : 'outlined'}>
            List
          </Button>
          <Button 
            startIcon={<Map />}
            onClick={handleClickMap} 
            variant={listOrMap === 'map' ? 'contained' : 'outlined'}>
            Map
          </Button>
          <SearchStyle
            value={filterName}
            onChange={onFilterName}
            placeholder="Search user..."
            variant="outlined"
            sx={{
              borderRadius: '25px',
              backgroundColor: 'background.paper',
            }}
            startAdornment={
              <InputAdornment position="start">
                <Iconify icon="eva:search-fill" sx={{ color: 'text.disabled', width: 20, height: 20 }} />
              </InputAdornment>
            }
          />
        </Stack>
      )}

      {numSelected > 0 ? (
        <Box display="flex" flexDirection="row" gap={1}>
          <Button 
              onClick={()=>setEditClientTagsModalOpen(true)}
              variant={'contained'}
              startIcon={<Add />}
          >
              Add Client Tag
          </Button>
          <Button 
              onClick={()=>setRemoveClientTagsModalOpen(true)}
              variant={'contained'}
              startIcon={<Remove />}
          >
              Remove Client Tag
          </Button> 
          <Tooltip title="Delete">
            <IconButton onClick={(event) => clickDelete(event, selectedClients)}>
              <Iconify icon="eva:trash-2-fill" />
            </IconButton>
          </Tooltip>
        </Box>
      ) : (
        <Box display="flex" flexDirection="row" gap={3}> 
          {/* Use 'gap' for spacing. Adjust '1' to the desired spacing value. */}
          <Button 
              onClick={()=>setCreateClientTagModalOpen(true)}
              variant={'outlined'}
              startIcon={<Add />}
          >
              Create Client Tag
          </Button>

          <CustomerDataFilter          
            customerDataFilters={customerDataFilters}
            product={product}
            minPrice={minPrice}
            setMinPrice={setMinPrice}
            maxPrice={maxPrice}
            setMaxPrice={setMaxPrice}
            minYear={minYear}
            setMinYear={setMinYear}
            maxYear={maxYear}
            setMaxYear={setMaxYear}
            equipInstallDateMin={equipInstallDateMin}
            setEquipInstallDateMin={setEquipInstallDateMin}
            equipInstallDateMax={equipInstallDateMax}
            setEquipInstallDateMax={setEquipInstallDateMax}
            statusFilters={statusFilters}
            setStatusFilters={setStatusFilters}
            tagFilters={tagFilters}
            setTagFilters={setTagFilters}
            zipCode={zipCode}
            setZipCode={setZipCode}
            city={city}
            setCity={setCity}
            state={state}
            setState={setState}
            customerSinceMin={customerSinceMin}
            setCustomerSinceMin={setCustomerSinceMin}
            customerSinceMax={customerSinceMax}
            setCustomerSinceMax={setCustomerSinceMax}
            minRooms={minRooms}
            setMinRooms={setMinRooms}
            maxRooms={maxRooms}
            setMaxRooms={setMaxRooms}
            minBaths={minBaths}
            setMinBaths={setMinBaths}
            maxBaths={maxBaths}
            setMaxBaths={setMaxBaths}
            minSqft={minSqft}
            setMinSqft={setMinSqft}
            maxSqft={maxSqft}
            setMaxSqft={setMaxSqft}
            minLotSqft={minLotSqft}
            setMinLotSqft={setMinLotSqft}
            maxLotSqft={maxLotSqft}
            setMaxLotSqft={setMaxLotSqft}
            savedFilter={savedFilter}
            setSavedFilter={setSavedFilter}
            uspsChanged={uspsChanged}
            setUspsChanged={setUspsChanged}
            minRevenue={minRevenue}
            setMinRevenue={setMinRevenue}
            maxRevenue={maxRevenue}
            setMaxRevenue={setMaxRevenue}
            clientTagFilters={clientTagFilters}
            setClientTagFilters={setClientTagFilters}
            clientTags={clientTags}
          />
        </Box>        
      )}
      {showAlert && (
        <Alert
          sx={{ mb: 2, mx: 'auto', width: '100%' }}
          variant="filled"
          severity="error"
          onClose={() => setShowAlert(false)}
        >
          Our customer map is a premium feature, please upgrade to access it.
        </Alert>
      )}
    <Dialog 
      open={createClientTagModalOpen} 
      onClose={()=>setCreateClientTagModalOpen(false)} 
      sx={{ padding: '2px', borderRadius: '15px', boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)' }}
      data-testid="create-client-tag-modal"
    >
        <DialogTitle>Add A Client Tag</DialogTitle>
        <FormikProvider value={formik}>
          <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
            <Stack spacing={3}>
              <TextField
                fullWidth                
                label="Client Tag"
                placeholder="Club Member"
                {...getFieldProps('clientTag')}
                error={Boolean(touched.clientTag && errors.clientTag)}
                helperText={touched.clientTag && errors.clientTag}
              />
            </Stack>
          </Form>
        </FormikProvider>
        <Stack direction="row" justifyContent="right">
          <Button color="error" onClick={()=>setCreateClientTagModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit}>Submit</Button>
        </Stack>
      </Dialog>
    <Dialog 
      open={editClientTagsModalOpen} 
      onClose={closeClientTagModal} 
      sx={{ padding: '2px', borderRadius: '15px', boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)' }}
      data-testid="edit-client-tag-modal"
      >
        <DialogTitle>Add Clients To Tag Groups</DialogTitle>        
        <Grid container spacing={1} sx={{padding: '10px'}}>
            {clientTags.map((option, index) => (                
                <Grid item key={index}>
                    <Box
                        component="label"
                        display="flex"
                        alignItems="center"
                        style={{
                            cursor: 'pointer',
                            padding: '5px',
                            borderRadius: '15px',
                            backgroundColor: tagColors[index % tagColors.length],
                            color: 'white',
                            fontWeight: 'bold',
                        }}
                    >
                        <Checkbox
                            checked={selectedClientTags.includes(option)}
                            onChange={handleSelectedClientTagsChange}
                            value={option}
                            style={{ color: 'white' }}
                        />
                        {capitalizeWords(option)}
                    </Box>
                </Grid>
            ))}
        </Grid>
        
        
        <Stack direction="row" justifyContent="right">
          <Button color="error" onClick={closeClientTagModal}>
            Cancel
          </Button>
          <Button onClick={addClientsToTagGroup}>Submit</Button>
        </Stack>
      </Dialog>
      <Dialog 
        open={removeClientTagsModalOpen} 
        onClose={closeClientTagModal} 
        sx={{ padding: '2px', borderRadius: '15px', boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)' }}
        data-testid="remove-client-tags-modal"
      >
        <DialogTitle>Remove Tags From Clients</DialogTitle>        
        <Grid container spacing={1} sx={{padding: '10px'}}>
            {clientTags.map((option, index) => (                
                <Grid item key={index}>
                    <Box
                        component="label"
                        display="flex"
                        alignItems="center"
                        style={{
                            cursor: 'pointer',
                            padding: '5px',
                            borderRadius: '15px',
                            backgroundColor: tagColors[index % tagColors.length],
                            color: 'white',
                            fontWeight: 'bold',
                        }}
                    >
                        <Checkbox
                            checked={selectedClientTags.includes(option)}
                            onChange={handleSelectedClientTagsChange}
                            value={option}
                            style={{ color: 'white' }}
                        />
                        {capitalizeWords(option)}
                    </Box>
                </Grid>
            ))}
        </Grid>
        
        
        <Stack direction="row" justifyContent="right">
          <Button color="error" onClick={closeClientTagModal}>
            Cancel
          </Button>
          <Button onClick={removeTagsFromClients}>Submit</Button>
        </Stack>
      </Dialog>
    </RootStyle>
  );
}
