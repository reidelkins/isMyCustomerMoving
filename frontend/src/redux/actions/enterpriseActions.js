import axios from 'axios';
import { createSlice } from '@reduxjs/toolkit';

import { DOMAIN } from '../constants';
import { getRefreshToken } from './usersActions';
import { login, loginError, loginLoading } from './authActions';

export const enterpriseSlice = createSlice({
  name: 'enterprise',
  initialState: {
    enterprise: {
      name: null,
      loading: false,
      error: null,
      companies: [],
    },
  },
  reducers: {
    enterpriseRequest: (state) => {
      state.enterprise.loading = true;
    },
    enterpriseSuccess: (state, action) => {
      state.enterprise.loading = false;
      state.enterprise.name = action.payload.name;
      state.enterprise.companies = action.payload.companies;
    },
    enterpriseFail: (state, action) => {
      state.enterprise.loading = false;
      state.enterprise.error = action.payload;
    },
  },
});

export const switchCompany = (company) => async (dispatch, getState) => {
  try {
    dispatch(loginLoading());
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.accessToken}`,
      },
    };

    const { data } = await axios.put(`${DOMAIN}/api/v1/accounts/enterprise/`, { company }, config);
    dispatch(login(data));
    localStorage.setItem('userInfo', JSON.stringify(data));
    dispatch(enterpriseAsync());
  } catch (error) {
    console.log(error.response.data);

    dispatch(
      loginError(
        // eslint-disable-next-line no-nested-ternary
        error.response && error.response.data.non_field_errors
          ? error.response.data.non_field_errors[0]
          : error.response && error.response.data.detail
          ? error.response.data.detail
          : error.message
      )
    );
  }
};

export const enterpriseAsync = () => async (dispatch, getState) => {
  try {
    dispatch(enterpriseRequest());
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.accessToken}`,
      },
    };
    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/enterprise/`, config);
    dispatch(enterpriseSuccess(data));
  } catch (error) {
    dispatch(enterpriseFail(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, enterpriseAsync()));
    }
  }
};

export const { enterpriseRequest, enterpriseSuccess, enterpriseFail } = enterpriseSlice.actions;
export const enterpriseInfo = (state) => state.enterprise.enterprise;
export default enterpriseSlice.reducer;
