import React, { useState } from 'react';
import PropTypes from 'prop-types';
import * as Yup from 'yup';
import {
  Button,  
  TextField,
  Grid,
} from '@mui/material';
import { useFormik } from 'formik';
import { useDispatch } from 'react-redux';

import { companyAsync } from '../redux/actions/authActions';
import GridSetting from './GridSetting';

ServiceTitanTags.propTypes = {
  userInfo: PropTypes.objectOf(PropTypes.any),
};

const EditTagBox = ({label, prop, getFieldProps}) => {  
  return (
    <Grid item xs={12} md={4}>
      <TextField
        label={label}
        {...getFieldProps(prop)}        
        />
    </Grid>
  )
}

export default function ServiceTitanTags({ userInfo }) {    
  const [editing, setEditing] = useState(false);

  const dispatch = useDispatch();  

  const IntegrateSTSchema = Yup.object().shape({
    tenantID: Yup.string("'"),
    clientID: Yup.string("'"),
    clientSecret: Yup.string("'"),
    forSale: Yup.string("'"),
    recentlySold: Yup.string(''),
    forSale_contacted: Yup.string(''),
    recentlySold_contacted: Yup.string(''),
  });

  const formik = useFormik({
    initialValues: {
      tenantID: userInfo.company.tenant_id ? userInfo.company.tenant_id : '',
      clientID: userInfo.company.client_id ? userInfo.company.client_id : '',
      clientSecret: userInfo.company.client_secret ? userInfo.company.client_secret : '',
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
          values.tenantID,
          values.clientID,
          values.clientSecret,
          values.forSale,
          values.forRent,
          values.recentlySold,
          values.forSale_contacted,
          values.recentlySold_contacted,
          values.forSaleDate,
          values.soldDate,
          '',
          '',
        )
      );
    },
  });

  const { values, handleSubmit, getFieldProps } = formik;
  const gridSettings = [
    {
      label: 'Tenant ID',
      value: userInfo.company.tenant_id,
      tooltip: 'This is the ID for your company on Service Titan.',
      step: 1,
    },
    {
      label: 'Client ID',
      value: userInfo.company.client_id,
      tooltip: 'This is the ID for the Is My Customer Moving App on Service Titan',
      step: 2,
    },
    {
      label: 'Client Secret',
      value: userInfo.company.client_secret,
      tooltip: 'This is the secret for the Is My Customer Moving App on Service Titan',
      step: 2,
    },
    {
      label: 'For Sale ID',
      value: userInfo.company.service_titan_for_sale_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that are for sale or have their home listed.',
      step: 3,
    },
    {
      label: 'For Sale Date',
      value: userInfo.company.service_titan_listed_date_custom_field_id,
      tooltip: 'This is the ID for the tag you created for your customers that are for sale or have their home listed.',
      step: 3,
    },
    {
      label: 'For Sale and Contacted ID',
      value: userInfo.company.service_titan_for_sale_contacted_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that are for sale or have their home listed and have been contacted.',
      step: 3,
    },
    {
      label: 'Recently Sold ID',
      value: userInfo.company.service_titan_recently_sold_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that have recently sold their home.',
      step: 3,
    },
    {
      label: 'Sold Date',
      value: userInfo.company.service_titan_sold_date_custom_field_id,
      tooltip: 'This is the ID for the tag you created for your customers that have recently sold their home.',
      step: 3,
    },
    {
      label: 'Recently Sold and Contacted ID',
      value: userInfo.company.service_titan_recently_sold_contacted_tag_id,
      tooltip: 'This is the ID for the tag you created for your customers that have recently sold their home and have been contacted.',
      step: 3,
    },
  ];    
  return (
    <div>      
      {editing ? (
          <Grid container spacing={3}>
            <EditTagBox label="Tenant ID" prop="tenantID" getFieldProps={getFieldProps} />
            {userInfo.company.tenant_id && (
              <>
                <EditTagBox label="Client ID" prop="clientID" getFieldProps={getFieldProps} />
                <EditTagBox label="Client Secret" prop="clientSecret" getFieldProps={getFieldProps} />
              </>
            )}
            {userInfo.company.tenant_id && userInfo.company.client_id && userInfo.company.client_secret && (
              <>
                <EditTagBox label="For Sale Tag" prop="forSale" getFieldProps={getFieldProps} />
                <EditTagBox label="Listed For Sale Date" prop="forSaleDate" getFieldProps={getFieldProps} />
                <EditTagBox label="For Sale and Contacted Tag" prop="forSale_contacted" getFieldProps={getFieldProps} />
                <EditTagBox label="Recently sold Tag" prop="recentlySold" getFieldProps={getFieldProps} />
                <EditTagBox label="Sold Date" prop="soldDate" getFieldProps={getFieldProps} />
                <EditTagBox label="Recently Sold and Contacted Tag" prop="recentlySold_contacted" getFieldProps={getFieldProps} />            
              </>
              )}            
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
          <>
            <Grid container spacing={3} onClick={() => setEditing(true)} style={{ cursor: 'pointer' }} >
              {          
                gridSettings
                  .filter((setting) => setting.step === 1)
                  .map((setting) => (
                    <GridSetting
                      key={setting.id}
                      label={setting.label}
                      value={setting.value}
                      tooltip={setting.tooltip}
                    />
                  ))
              }
              {userInfo.company.tenant_id &&
                gridSettings
                  .filter((setting) => setting.step === 2)
                  .map((setting) => (
                    <GridSetting
                      key={setting.id}
                      label={setting.label}
                      value={setting.value}
                      tooltip={setting.tooltip}
                    />
                  ))
              }
              {userInfo.company.tenant_id &&
                gridSettings
                  .filter((setting) => setting.step === 3)
                  .map((setting) => {                  
                    return (
                    <GridSetting
                      key={setting.id}
                      label={setting.label}
                      value={setting.value}
                      tooltip={setting.tooltip}
                    />
                  )})
              }
            </Grid>
            <Button size="large" variant="contained" onClick={() => setEditing(true)} data-testid="edit-profile">
              Edit
            </Button>
          </>
        )}      
    </div>
  );
}
