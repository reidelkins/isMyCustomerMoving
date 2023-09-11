import React, { useState } from 'react';
import PropTypes from 'prop-types';
import * as Yup from 'yup';
import {
  Button,
  IconButton,
  TextField,
  Grid,
  Modal,
  Fade,
  Box,
  Typography,
} from '@mui/material';
import { useFormik } from 'formik';
import { useDispatch } from 'react-redux';

import { companyAsync } from '../redux/actions/authActions';
import GridSetting from './GridSetting';
import Iconify from './Iconify';

ServiceTitanTagsModal.propTypes = {
  userInfo: PropTypes.objectOf(PropTypes.any),
};

export default function ServiceTitanTagsModal({ userInfo }) {  
  const [integrateInfo, setIntegrateInfo] = useState(false);
  const [editing, setEditing] = useState(false);

  const dispatch = useDispatch();  

  const IntegrateSTSchema = Yup.object().shape({
    forSale: Yup.string("'"),
    recentlySold: Yup.string(''),
    forSale_contacted: Yup.string(''),
    recentlySold_contacted: Yup.string(''),
  });

  const formik = useFormik({
    initialValues: {
      forSale: userInfo.company.service_titan_for_sale_tag_id ? userInfo.company.service_titan_for_sale_tag_id : '',
      forRent: '',
      recentlySold: userInfo.company.service_titan_recently_sold_tag_id
        ? userInfo.company.service_titan_recently_sold_tag_id
        : '',
      forSale_contacted: userInfo.company.service_titan_for_sale_contacted_tag_id
        ? userInfo.company.service_titan_for_sale_contacted_tag_id
        : '',
      recentlySold_contacted: userInfo.company.service_titan_recently_sold_contacted_tag_id
        ? userInfo.company.service_titan_recently_sold_contacted_tag_id
        : '',
      forSaleDate: userInfo.company.service_titan_listed_date_custom_field_id
        ? userInfo.company.service_titan_listed_date_custom_field_id
        : '',
      soldDate: userInfo.company.service_titan_sold_date_custom_field_id
        ? userInfo.company.service_titan_sold_date_custom_field_id
        : '',
    },
    validationSchema: IntegrateSTSchema,
    onSubmit: () => {
      setEditing(false);
      dispatch(
        companyAsync(
          '',
          '',
          '',
          '',
          '',
          values.forSale,
          values.forRent,
          values.recentlySold,
          values.forSale_contacted,
          values.recentlySold_contacted,
          values.forSaleDate,
          values.soldDate,
          ''
        )
      );
    },
  });

  const { values, handleSubmit, getFieldProps } = formik;
  const gridSettings = [
    {
      label: 'For Sale ID',
      value: userInfo.company.service_titan_for_sale_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that are for sale or have their home listed.',
    },
    {
      label: 'For Sale Date',
      value: userInfo.company.service_titan_listed_date_custom_field_id,
      tooltip: 'This is the ID for the tag you created for your customers that are for sale or have their home listed.',
    },
    {
      label: 'For Sale and Contacted ID',
      value: userInfo.company.service_titan_for_sale_contacted_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that are for sale or have their home listed and have been contacted.',
    },
    {
      label: 'Recently Sold ID',
      value: userInfo.company.service_titan_recently_sold_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that have recently sold their home.',
    },
    {
      label: 'Sold Date',
      value: userInfo.company.service_titan_sold_date_custom_field_id,
      tooltip: 'This is the ID for the tag you created for your customers that have recently sold their home.',
    },
    {
      label: 'Recently Sold and Contacted ID',
      value: userInfo.company.service_titan_recently_sold_contacted_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that have recently sold their home and have been contacted.',
    },
  ];
  return (
    <div>      
      {editing ? (
        <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="text"
                label="For Sale Tag"
                {...getFieldProps('forSale')}                                
              />
            </Grid>            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="text"
                label="Listed For Sale Date"
                {...getFieldProps('forSaleDate')}                                
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="text"
                label="For Sale and Contacted Tag "
                {...getFieldProps('forSale_contacted')}                                
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="text"
                label="Recently sold Tag"
                {...getFieldProps('recentlySold')}                                
              />
            </Grid>            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="text"
                label="Sold Date"
                {...getFieldProps('soldDate')}                                
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="text"
                label="Recently Sold and Contacted Tag "
                {...getFieldProps('recentlySold_contacted')}                                
              />
            </Grid>
            <Grid item xs={6} md={4}>
              <Button
                fullWidth
                size="large"
                variant="contained"
                color="error"
                onClick={() => setEditing(false)}
                data-testid="cancel-profile-button"
              >
                Cancel
              </Button>
            </Grid>

            <Grid item xs={6} md={4}>
              <Button
                fullWidth
                size="large"
                type="submit"
                variant="contained"
                data-testid="update-profile-button"
                onClick={handleSubmit}
              >
                Save Changes
              </Button>
            </Grid>
          </Grid>
        ):(                  
          <Grid container spacing={3} onClick={() => setEditing(true)} style={{ cursor: 'pointer' }} >
            {gridSettings.map((setting) => (
              <GridSetting 
                key={setting.id}
                label={setting.label} 
                value={setting.value}
                tooltip={setting.tooltip}
              />
            ))
            }
            

                  
          </Grid>
        )}
      <IconButton onClick={() => setIntegrateInfo(true)}>
        <Iconify icon="bi:question-circle-fill" />
      </IconButton>      
      <Modal
        open={integrateInfo}
        onClose={() => setIntegrateInfo(false)}
        closeAfterTransition
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
        padding="10"
      >
        <Fade in={integrateInfo}>
          <Box
            sx={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: 400,
              bgcolor: 'white',
              border: '2px solid #000',
              boxShadow: '24px',
              p: '4%',
            }}
          >
            <Typography id="modal-modal-title" variant="h5" component="h2">
              Add Service Titan Tag IDs Instructions
            </Typography>
            <Typography id="modal-modal-description" sx={{ mt: 2 }}>
              1. Adding Tag IDs will enable automatically updating your customer list on service titan with the
              information found from IMCM <br />
              <br />
              2. First to make a new tag, log in to service titan, go to settings, search for tag, and click tag types,
              then click add. <br />
              <br />
              3. Next choose a color, a name (like "For Sale or Home Listed"), then click save. <br />
              <br />
              4. You then need to scroll the list of tags to find the one you just made. Once found, click the edit
              button on the row of that tag. <br />
              <br />
              5. Copy the ID number from the URL. It will be a long number like 1234567890. <br />
              <br />
              <br />
              Note: You can make 2 different tags for this data or you can make one tag and use the same ID for all 2.
              <br />
              The last two tags are so you can keep track on Service Titan once you have marked a client as contacted
              within our system and differentiate your marketing campaigns with this data. Click{' '}
              <a href="https://www.loom.com/share/523b171ab81e47f2a050e1b28704c30e" target="_blank" rel="noreferrer">
                here{' '}
              </a>{' '}
              to see a video walking through this process.
            </Typography>
          </Box>
        </Fade>
      </Modal>
    </div>
  );
}
