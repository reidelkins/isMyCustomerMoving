import axios from 'axios';
import {
  LOGIN_REQUEST,
  LOGIN_SUCCESS,
  LOGIN_FAIL,
  REGISTER_REQUEST,
  REGISTER_SUCCESS,
  REGISTER_FAIL,
  LOGOUT,
  RESET_REQUEST_REQUEST,
  RESET_REQUEST_SUCCESS,
  RESET_REQUEST_FAIL,
  PASSWORD_RESET_REQUEST,
  PASSWORD_RESET_SUCCESS,
  PASSWORD_RESET_FAIL,
} from '../types/auth';
import {
  ADDUSER_REQUEST, 
  ADDUSER_SUCCESS, 
  ADDUSER_FAIL,
} from '../types/users';

import { DOMAIN } from '../constants';

export const submitNewPass = (password, token) => async (dispatch) => {
  try {
    dispatch({
      type: PASSWORD_RESET_REQUEST,
    });

    const config = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const { data } = await axios.post(
      `${DOMAIN}/api/v1/accounts/password_reset/confirm/`,
      { 
        token,
        password
      },
      config
    );

    dispatch({
      type: PASSWORD_RESET_SUCCESS,
      payload: data,
    });
  } catch (error) {
    dispatch({
      type: PASSWORD_RESET_FAIL,
      payload:
        error.response && error.response.data.message
          ? error.response.data.message
          : error.message,
    });
  }
};

export const login = (email, password) => async (dispatch) => {
  try {
    dispatch({
      type: LOGIN_REQUEST,
    });

    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };

    const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/login/`, { email, password }, config);

    dispatch({
      type: LOGIN_SUCCESS,
      payload: data,
    });

    localStorage.setItem('userInfo', JSON.stringify(data));
  } catch (error) {
    dispatch({
      type: LOGIN_FAIL,
      payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
    });
  }
};

export const register = (company, accessToken, firstName, lastName, email, password) => async (dispatch) => {
  try {
    dispatch({
      type: REGISTER_REQUEST,
    });

    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };

    const { data } = await axios.post(
      `${DOMAIN}/api/v1/accounts/register/`,
      { firstName, lastName, email, password, company, accessToken },
      config
    );

    dispatch({
      type: REGISTER_SUCCESS,
      payload: data,
    });

    dispatch({
      type: LOGIN_SUCCESS,
      payload: data,
    });

    localStorage.setItem('userInfo', JSON.stringify(data));
  } catch (error) {
    dispatch({
      type: REGISTER_FAIL,
      payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
    });
  }
};

export const addUser = (firstName, lastName, email, password, token) => async (dispatch) => {
  try {
    dispatch({
      type: ADDUSER_REQUEST,
    });
    console.log(email)
    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };

    const { data } = await axios.post(
      `${DOMAIN}/api/v1/accounts/manageuser/${token}/`,
      { firstName, lastName, email, password },
      config
    );

    dispatch({
      type: ADDUSER_SUCCESS,
      payload: data,
    });

    dispatch({
      type: ADDUSER_SUCCESS,
      payload: data,
    });
    
  } catch (error) {
    dispatch({
      type: ADDUSER_FAIL,
      payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
    });
  }
};

export const logout = () => (dispatch) => {
  localStorage.removeItem('userInfo');
  dispatch({ type: LOGOUT });
};

export const resetRequest = (email, company) => async (dispatch) => {
  try {
    dispatch({
      type: RESET_REQUEST_REQUEST,
    });

    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };

    const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/password_reset/`, { email, company }, config);

    dispatch({
      type: RESET_REQUEST_SUCCESS,
      payload: data,
    });

    localStorage.setItem('userInfo', JSON.stringify(data));
  } catch (error) {
    dispatch({
      type: RESET_REQUEST_FAIL,
      payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
    });
  }
};
