import axios from 'axios';
import { createSlice } from '@reduxjs/toolkit';

import { DOMAIN } from '../constants';

export const authSlice = createSlice({
  name: "auth",
  initialState: {
    userInfo: {
      userInfo: localStorage.getItem('userInfo') ? JSON.parse(localStorage.getItem('userInfo')) : null,
      loading: false,
      error: null,
    },
    registerInfo: {
      loading: false,
      error: null,
    },
  },
  reducers: {
    // -----------------  AUTH  -----------------
    login: (state, action) => {
      state.userInfo.userInfo = action.payload;
      state.userInfo.error = null;
      state.userInfo.loading = false;
    },
    loginError: (state, action) => {
      state.userInfo.error = action.payload;
      state.userInfo.loading = false;
    },
    loginLoading: (state) => {
      state.userInfo.loading = true;
    },
    register: (state, action) => {
      state.userInfo.userInfo = action.payload;
      state.registerInfo.error = null;
      state.registerInfo.loading = false;
    },
    registerError: (state, action) => {
      state.registerInfo.error = action.payload;
      state.registerInfo.loading = false;
    },
    registerLoading: (state) => {
      state.registerInfo.loading = true;
    },
    reset: (state) => {
      state.registerInfo.error = null;
      state.registerInfo.loading = false;
    },
    logoutUser: (state) => {
      state.userInfo = {
        userInfo: null,
        loading: false,
        error: null,
      };
    },
    company: (state, action) => {
      state.userInfo.userInfo = action.payload;
      state.userInfo.loading = false;
      state.userInfo.error = null;
    },
    companyError: (state, action) => {
      state.userInfo.error = action.payload;
      state.userInfo.loading = false;
    },
    companyLoading: (state) => {
      state.userInfo.loading = true;
    },

  }
});

export const loginAsync = (email, password) => async (dispatch) => {
  try {
    dispatch(loginLoading()); 
    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };
    const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/login/`, { email, password }, config);
    dispatch(login(data));
    localStorage.setItem('userInfo', JSON.stringify(data));
  } catch (error) {
    dispatch(loginError(error.response && error.response.data.detail ? error.response.data.detail : error.message,));
  }
};

export const registerAsync = (company, accessToken, firstName, lastName, email, password) => async (dispatch) => {
  try {
    dispatch(registerLoading());
    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };
    const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/register/`, { company, accessToken, firstName, lastName, email, password }, config);    
    dispatch(register(data));
    localStorage.setItem('userInfo', JSON.stringify(data));
  } catch (err) {
    dispatch(registerError(err.response && err.response.data.detail ? err.response.data.detail : err.message,));
  }
};

export const companyAsync = (userInfo, email, phone, tenantID, clientID, clientSecret) => async (dispatch, getState) => {
  try {
    dispatch(companyLoading());

    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };
    const { data } = await axios.put(
      `${DOMAIN}/api/v1/accounts/company/`,
      { 'company': userInfo.company.id, email, phone, tenantID, clientID, clientSecret, 'user': userInfo.id},
      config
    );
    dispatch(company(data));
    localStorage.setItem('userInfo', JSON.stringify(data));
  } catch (err) {
    console.log(err)
    dispatch(companyError(err.response && err.response.data.detail ? err.response.data.detail : err.message,));
  }
};

export const resetPasswordAsync = (oldPassword, password) => async (dispatch) => {
};

export const addUserAsync = (firstName, lastName, email, password, token) => async (dispatch) => {
  try {
    dispatch(registerAsync());
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
    // dispatch(addUser(data));
    localStorage.setItem('userInfo', JSON.stringify(data));
  } catch (err) {
    dispatch(registerError(err.response && err.response.data.detail ? err.response.data.detail : err.message,));
  }
};

export const resetAsync = (email) => async (dispatch) => {
  try {
    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };
    dispatch(registerLoading());
    await axios.post(`${DOMAIN}/api/v1/accounts/password_reset/`, { email }, config);
    dispatch(reset());
  } catch (err) {
    dispatch(registerError(err.response && err.response.data.detail ? err.response.data.detail : err.message,));
  }
};

export const submitNewPassAsync = (password, token) => async (dispatch) => {
  try {
    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };

    dispatch(registerLoading());
    await axios.post(
      `${DOMAIN}/api/v1/accounts/password_reset/confirm/`,
      { 
        token,
        password
      },
      config
    );
  } catch (err) {
    dispatch(registerError(err.response && err.response.data.detail ? err.response.data.detail : err.message,));
  }
};

export const logout = () => (dispatch) => {
  localStorage.removeItem('userInfo');
  dispatch(logoutUser());
};

export const { login, loginError, loginLoading, register, registerError, registerLoading, logoutUser, company, companyError, companyLoading, reset } = authSlice.actions;
export const showLoginInfo = (state) => state.auth.userInfo;
export const showRegisterInfo = (state) => state.auth.registerInfo;
export default authSlice.reducer;

// export const addUserOld = (firstName, lastName, email, password, token) => async (dispatch) => {
//   try {
//     dispatch({
//       type: ADDUSER_REQUEST,
//     });
//     console.log(email)
//     const config = {
//       headers: {
//         'Content-type': 'application/json',
//       },
//     };

//     const { data } = await axios.post(
//       `${DOMAIN}/api/v1/accounts/manageuser/${token}/`,
//       { firstName, lastName, email, password },
//       config
//     );

//     dispatch({
//       type: ADDUSER_SUCCESS,
//       payload: data,
//     });

//     dispatch({
//       type: ADDUSER_SUCCESS,
//       payload: data,
//     });
    
//   } catch (error) {
//     dispatch({
//       type: ADDUSER_FAIL,
//       payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
//     });
//   }
// };

// export const resetRequestOld = (email) => async (dispatch) => {
//   try {
//     dispatch({
//       type: RESET_REQUEST_REQUEST,
//     });

//     const config = {
//       headers: {
//         'Content-type': 'application/json',
//       },
//     };

//     const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/password_reset/`, { email }, config);

//     dispatch({
//       type: RESET_REQUEST_SUCCESS,
//       payload: data,
//     });
//   } catch (error) {
//     dispatch({
//       type: RESET_REQUEST_FAIL,
//       payload: error.response && error.response.data.detail ? error.response.data.detail : error.message,
//     });
//   }
// };

// export const submitNewPassOld = (password, token) => async (dispatch) => {
//   try {
//     dispatch({
//       type: PASSWORD_RESET_REQUEST,
//     });

//     const config = {
//       headers: {
//         'Content-Type': 'application/json',
//       },
//     };

//     await axios.post(
//       `${DOMAIN}/api/v1/accounts/password_reset/confirm/`,
//       { 
//         token,
//         password
//       },
//       config
//     );

//     dispatch({
//       type: PASSWORD_RESET_SUCCESS,
//     });
//   } catch (error) {
//     dispatch({
//       type: PASSWORD_RESET_FAIL,
//       payload:
//         error.response && error.response.data.message
//           ? error.response.data.message
//           : error.message,
//     });
//   }
// };
