import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Papa from 'papaparse';
import PropTypes from 'prop-types';
import {
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  Grid,
  IconButton,
  Backdrop,
  Box,
  Fade,
  Modal,
} from '@mui/material';
import { makeStyles } from '@mui/styles';
import Iconify from './Iconify';
import { uploadClientsAsync, selectClients, uploadServiceAreasAsync } from '../redux/actions/usersActions';

const useStyles = makeStyles(() => ({
  uploaderDiv: {
    backgroundColor: '#f1f0ef',
    height: '80px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '5px',
  },
}));



const FileUploader = ({ fileType }) => {
  const dispatch = useDispatch();
  const classes = useStyles();

  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [error, setError] = useState(null);
  const [uploaded, setUploaded] = useState(false);
  const [headers, setHeaders] = useState([]);
  const [uploadInfo, setUploadInfo] = useState(false);
  const [headerMappings, setHeaderMappings] = useState({
    name: '',
    address: '',
    city: '',
    state: '',
    'zip code': '',
    'phone number': '',
  });

  const listClient = useSelector(selectClients);
  const { loading } = listClient;

  const exportTemplate = () => {
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'Customer Name,Street Address,City,State,ZipCode,Phone\r\n';
    csvContent += `Example Name, 123 Main St, Nashville, TN, 12345, 8882224444\r\n`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    const docName = `isMyCustomerMoving_template`;
    link.setAttribute('download', `${docName}.csv`);
    document.body.appendChild(link); // Required for FF
    link.click();
    document.body.removeChild(link);
    setUploadInfo(false);
  };

  const handleFileChange = async ({ target }) => {
    setFile(target.files[0]);
    setFileName(target.files[0].name);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    handleFileChange({
      target: {
        files: [file],
      },
    });
  };

  const handleDragOver = (event) => {
    event.stopPropagation();
    event.preventDefault();
  };

  useEffect(() => {
    async function fetchData() {
      if (!file) return;
      const fileData = await readFile(file);
      const lowerCaseHeaders = Object.keys(fileData[0]).map((header) => header.toLowerCase());
      setHeaders(lowerCaseHeaders);
      const fileType = file.name.split('.').pop();
      if (fileType !== 'csv' && fileType !== 'xlsx' && fileType !== 'xls' && fileType !== 'xlsm') {
        setError('Invalid file type');
        setFile(null);
      } else {
        setError(null);
      }
    }

    fetchData();
  }, [file]);

  useEffect(() => {
    if (fileType === "ServiceArea") {
      setHeaderMappings({
        Zip_Code: '',
      });      
    }
  }, [fileType]);

  // eslint-disable-next-line arrow-body-style
  const readFile = (file) => {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        complete: (results) => {
          resolve(results.data);
        },
        error: (error) => {
          reject(error);
        },
      });
    });
  };

  const handleHeaderMappingChange = (event) => {
    const { name, value } = event.target;
    setHeaderMappings({
      ...headerMappings,
      [name]: value,
    });
  };

  const handleSubmit = async (event) => {
    let e = false;
    setError(null);
    event.preventDefault();

    Object.keys(headerMappings).forEach((header) => {
      const selectElement = event.target.elements[header];
      if (selectElement.value === '') {
        setError('Please select a value for all fields');
        e = true;
      }
    });

    if (!file) {
      setError('No file selected');
      e = true;
    }
    const fileType = file.name.split('.').pop();
    if (fileType !== 'csv' && fileType !== 'xlsx') {
      setError('Invalid file type');
      e = true;
    }

    try {
      if (e) {
        return;
      }
      const fileData = await readFile(file);
      const data = fileData.map((row) => {
        const newRow = {};
        Object.keys(row).forEach((key) => {
          Object.keys(headerMappings).forEach((header) => {
            const selectElement = event.target.elements[header];
            if (key.toLowerCase() === selectElement.value.toLowerCase()) {
              newRow[header] = row[key];
            }
          });
        });
        return newRow;
      });
      await sendData(data);
      setUploaded(true);
      setFile(null);
    } catch (err) {
      setError('Error reading file');
    }
  };

  const sendData = (data) => {
    if (fileType === "ClientFile") {
      dispatch(uploadClientsAsync(data));
    } else if (fileType === "ServiceArea") {
      dispatch(uploadServiceAreasAsync(data));
    }
  };

  return (
    <div>
      {!loading && (
        <>
          <form onSubmit={handleSubmit}>
            <div
              onDrop={(event) => handleDrop(event)}
              onDragOver={(event) => handleDragOver(event)}
              className={classes.uploaderDiv}
            >
              <label htmlFor="file" style={{ cursor: 'pointer', textDecoration: 'underline' }}>
                {!file && uploaded && `Success! ${fileName} has been uploaded.`}
                {file && `Uploading ${fileName}`}
                {!file && !uploaded && fileType === "ClientFile" && 'Upload Your Client List'}
                {!file && !uploaded && fileType === "ServiceArea" && 'Upload Your Service Areas'}
              </label>
              <input
                type="file"
                id="file"
                accept=".csv, .xlsx, .xls, .xlsm"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>
            <Grid container spacing={3}>
              {file &&
                Object.keys(headerMappings).map((header) => (
                  <Grid item xs={12} sm={6} md={4} key={header}>
                    <Typography style={{ width: '100px' }}>{header}</Typography>
                    <div>
                      <FormControl>
                        <InputLabel id="inputLabel">
                          {headers.includes(header.toLowerCase()) ? header : 'Choose Header'}
                        </InputLabel>
                        <Select
                          labelId="inputLabel"
                          name={header}
                          onChange={handleHeaderMappingChange}
                          value={headers.includes(header.toLowerCase()) ? header : headerMappings[header]}
                          style={{ minWidth: '200px' }}
                        >
                          <MenuItem value={headers.includes(header.toLowerCase()) ? header : ''} />
                          {header !== 'phone number'
                            ? headers.map((headerName) => (
                                <MenuItem key={headerName} value={headerName}>
                                  {headerName}
                                </MenuItem>
                              ))
                            : [...headers, 'None'].map((headerName) => (
                                <MenuItem key={headerName} value={headerName}>
                                  {headerName}
                                </MenuItem>
                              ))}
                        </Select>
                      </FormControl>
                    </div>
                  </Grid>
                ))}
            </Grid>

            {file && (
              <Button type="submit" variant="contained">
                Submit
              </Button>
            )}
            {error && <p style={{ color: 'red' }}>{error}</p>}
          </form>

          <br />
          {fileType === "clientFile" && !file && !uploaded && (
            <IconButton onClick={() => setUploadInfo(true)}>
              <Iconify icon="bi:question-circle-fill" />
            </IconButton>
          )}
        </>
      )}
      {/* {(progress.complete && progress.deleted > 0) && (
        <div>
          <Typography style={{color:'red'}}>{progress.deleted} clients were not uploaded due to your subscription tier.</Typography>
          <Button variant="contained" color="primary" aria-label="Create Company" component="label">
              <Link href="https://billing.stripe.com/p/login/aEU2aZ4PtbdD9A49AA" color="secondary" underline="none" target="_blank" rel="noopener noreferrer">
                Upgrade Here
              </Link>
          </Button>
        </div>
      )} */}

      <Modal
        open={uploadInfo}
        onClose={() => setUploadInfo(false)}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{
          timeout: 500,
        }}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
        padding="10"
      >
        <Fade in={uploadInfo}>
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
              How To Upload Your Client List
            </Typography>
            <Typography id="modal-modal-description" sx={{ mt: 2 }}>
              Please upload a csv or excel file with the following columns:
              <br />
              <br />
              <b>Client Name</b> <br />
              <b>Street Address</b> <br />
              <b>City</b> <br />
              <b>State</b> <br />
              <b>Zip Code</b> <br />
              <b>Phone Number (Optional)</b> <br />
              <br />
              You can match your column headers to the above names after you choose your file and then just click
              submit! <br />
              <br />
            </Typography>
            <Button onClick={exportTemplate} variant="contained">
              Download Template Here
            </Button>
          </Box>
        </Fade>
      </Modal>
    </div>
  );
};

FileUploader.propTypes = {
  fileType: PropTypes.any
};

export default FileUploader;
