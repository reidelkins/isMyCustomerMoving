import React from 'react';
import * as Yup from 'yup';
import { Button, TextField, Dialog, DialogTitle, Stack } from '@mui/material';
import { useFormik, Form, FormikProvider } from 'formik';
import { useDispatch } from 'react-redux';

import { addUser } from '../redux/actions/usersActions';

export default function NewUserModal() {
  // const classes = useStyles();
  const [open, setOpen] = React.useState(false);
  const dispatch = useDispatch();

  const handleOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  const NewUserSchema = Yup.object().shape({
    email: Yup.string().email('Email must be a valid email address').required('Email is required'),
  });

  const formik = useFormik({
    initialValues: {
      email: '',
    },
    validationSchema: NewUserSchema,
    onSubmit: () => {
      dispatch(addUser(values.email));
      values.email = '';
      setOpen(false);
    },
  });

  const { errors, touched, values, handleSubmit, getFieldProps } = formik;
  return (
    <div>
      <Button variant="contained" color="primary" aria-label="Create Company" component="label" onClick={handleOpen}>
        Add User
      </Button>
      <Dialog open={open} onClose={handleClose} sx={{ padding: '2px' }}>
        <DialogTitle>Add a User</DialogTitle>
        <FormikProvider value={formik}>
          <Form autoComplete="off" noValidate onSubmit={handleSubmit}>
            <Stack spacing={3}>
              <TextField
                fullWidth
                // type="email"
                label="New User Email"
                placeholder="Email"
                {...getFieldProps('email')}
                error={Boolean(touched.email && errors.email)}
                helperText={touched.email && errors.email}
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
      </Dialog>
    </div>
  );
}
