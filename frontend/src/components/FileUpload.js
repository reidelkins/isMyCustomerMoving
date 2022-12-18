import { useState } from 'react';
import PropTypes from 'prop-types';

import {
  IconButton,
  Backdrop,
  Box,
  Fade,
  Modal,
  Button,
  Typography,
} from '@mui/material';
import { FilePond } from 'react-filepond';
import '../filepond.css';
import { DOMAIN } from '../redux/constants';
import Iconify from './Iconify';

FileUpload.propTypes = {
    userInfo: PropTypes.objectOf(PropTypes.any),
};

function FileUpload({userInfo}) {
    const [files, setFiles] = useState([]);
    const [uploadInfo, setUploadInfo] = useState(false);

    const exportTemplate = () => {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += 'Customer Name,Street Address,City,State,ZipCode\r\n';
        csvContent += `Example Name, 123 Main St, Nashville, TN, 12345\r\n`
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        const docName = `isMyCustomerMoving_template`
        link.setAttribute('download', `${docName}.csv`);
        document.body.appendChild(link); // Required for FF
        link.click();
        document.body.removeChild(link);
        setUploadInfo(false);
    };

    return(
        <>
            {userInfo.status === 'admin' && (
                <>
                <FilePond
                    files={files}
                    onupdatefiles={setFiles}
                    allowRevert='false'
                    maxFiles={1}
                    server={`${DOMAIN}/api/v1/accounts/upload/`}
                    name={`${userInfo.company}`}
                    labelIdle=' <span class="filepond--label-action">Upload Your Client List</span>'
                    credits='false'
                    storeAsFile='true'
                    labelFileProcessingComplete='Success! Moving data might take up to 30 minutes depending on the size of your list.'
                    checkValidity='true'
                    dropOnPage='true'
                    // acceptedFileTypes={['image/png', 'image/jpeg']}
                />
                <IconButton onClick={()=>setUploadInfo(true)} >
                    <Iconify icon="bi:question-circle-fill" />
                </IconButton>
                
                </>
            )}
            <Modal
                open={uploadInfo}
                onClose={()=>setUploadInfo(false)}
                closeAfterTransition
                BackdropComponent={Backdrop}
                BackdropProps={{
                timeout: 500,
                }}
                aria-labelledby="modal-modal-title"
                aria-describedby="modal-modal-description"
                padding='10'
            >
                <Fade in={uploadInfo}>
                <Box sx={{position:'absolute', top:'50%', left:'50%', transform:'translate(-50%, -50%)', width:400, bgcolor:'white', border:'2px solid #000', boxShadow: '24px', p:'4%'}}>
                    <Typography id="modal-modal-title" variant="h5" component="h2">
                    How To Upload Your Client List
                    </Typography>
                    <Typography id="modal-modal-description" sx={{ mt: 2 }}>
                    Our upload format requires a CSV file with the following headers:
                    <br />
                    <b>(Client) Name</b> <br />
                    <b>Street Address</b> <br />
                    <b>City</b> <br />
                    <b>State</b> <br />
                    <b>Zip Code</b> <br /><br />

                    </Typography>
                    <Button onClick={exportTemplate} variant="contained">
                        Download Template Here
                    </Button>
                </Box>
                </Fade>
            </Modal>
        </>
    )
}

export default FileUpload;