import axios from 'axios';
import { UPLOAD_REQUEST, UPLOAD_SUCCESS, UPLOAD_FAIL } from '../types/users';
import { DOMAIN } from '../constants';

export const uploadClients = (file) => async (dispatch, getState) => {
    const formData = new FormData();
  try {
    dispatch({
      type: UPLOAD_REQUEST,
    });

    const {
      userLogin: { userInfo },
    } = getState();
    console.log("This is the user info that you asked for")
    console.log(userInfo)

    
    formData.append("csv", file);
    const config = {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${userInfo.access}`,
      },
    };

    // const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/upload/`,
    //     {'form':formData, 'company':userInfo.company},
    //     config);

    dispatch({
      type: UPLOAD_SUCCESS,
      payload: "data",
    });
  } catch (error) {
    dispatch({
      type: UPLOAD_FAIL,
      payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
    });
  }
  
};