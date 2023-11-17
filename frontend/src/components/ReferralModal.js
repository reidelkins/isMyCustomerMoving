import React, { useState } from 'react';
import { Button, TextField, Dialog, DialogTitle, DialogContent, Stack, Divider } from '@mui/material';
import { orange, grey } from '@mui/material/colors';
import { useFormik, Form, FormikProvider } from 'formik';
import { useDispatch } from 'react-redux';
import PropTypes from 'prop-types';
import * as Yup from 'yup';

import { makeReferralAsync } from '../redux/actions/usersActions';

ReferralModal.propTypes = {
  id: PropTypes.string,
  alreadyReferred: PropTypes.bool,
};

export default function ReferralModal({ id, alreadyReferred }) {
  const [open, setOpen] = useState(false);
  const [referred, setReferred] = useState(alreadyReferred);
  const dispatch = useDispatch();

  const handleOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  const ReferralSchema = Yup.object().shape({
    area: Yup.string('')
      .required('Please input a city name or valid zip code')
      .matches(
        // regex for zip code or city name, zip code should be 5 digits and city name should be all letters with no numbers
        /^(?:\d{5}|[a-zA-Z]+(?:[\s-][a-zA-Z]+)*)$/,
        'Must be a valid zip code or city name'
      ),
  });

  const formik = useFormik({
    initialValues: {
      area: '',
    },
    validationSchema: ReferralSchema,
    onSubmit: () => {
      dispatch(makeReferralAsync(id, values.area));
      setOpen(false);
      setReferred(true);
    },
  });

  const { errors, touched, values, handleSubmit, getFieldProps } = formik;
  return (
    <div>
      <Button
        variant="contained"
        sx={{
          bgcolor: referred ? grey[500] : orange[300],
          '&:hover': {
            bgcolor: referred ? grey[500] : orange[700],
          },
        }}
        onClick={handleOpen}
        disabled={referred}
      >
        {referred ? 'Referred' : 'Refer'}
      </Button>
      <Dialog open={open} onClose={handleClose} sx={{ padding: '2px', borderRadius: '15px', boxShadow: '0 4px 20px 0 rgba(0,0,0,0.12)' }} >
        <DialogTitle>Refer Customer</DialogTitle>
        <Divider />
        <DialogContent>
          <p>Is your customer moving out of your area? Refer them to another dealer within your network!</p>
          <br />
          <FormikProvider value={formik}>
            <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
              <Stack spacing={3}>
                <TextField
                  fullWidth
                  defaultValue="Enter City or Zip Code"
                  label="City/Zip Code"
                  {...getFieldProps('area')}
                  error={Boolean(touched.area && errors.area)}
                  helperText={touched.area && errors.area}
                />
              </Stack>
            </Form>
          </FormikProvider>
          <Stack direction="row" justifyContent="right">
            <Button color="error" onClick={handleClose}>
              Cancel
            </Button>
            <Button onClick={handleSubmit}>Submit</Button>
          </Stack>
        </DialogContent>
      </Dialog>
    </div>
  );
}
