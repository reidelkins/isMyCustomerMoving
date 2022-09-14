import axios from 'axios';
import { LIST_REQUEST, LIST_SUCCESS, LIST_FAIL, STATUS_REQUEST, STATUS_SUCCESS, STATUS_FAIL } from '../types/users';
import { DOMAIN } from '../constants';

export const users = () => async (dispatch, getState) => {
  try {
    dispatch({
      type: LIST_REQUEST,
    });

    const {
      userLogin: { userInfo },
    } = getState();

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };

    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/clients/${userInfo.company}`, config);

    dispatch({
      type: LIST_SUCCESS,
      payload: data,
    });
  } catch (error) {
    dispatch({
      type: LIST_FAIL,
      payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
    });
  }
};

export const update = () => async (dispatch, getState) => {
  try {
    dispatch({
      type: STATUS_REQUEST,
    });

    const {
      userLogin: { userInfo },
    } = getState();

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };

    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/update/${userInfo.company}`, config);
    console.log(data)
    console.log("blah")
    dispatch({
      type: STATUS_SUCCESS,
      payload: data,
    });
  } catch (error) {
    dispatch({
      type: STATUS_FAIL,
      payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
    });
  }
};
