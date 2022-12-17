/* eslint-disable default-param-last */
import { createSlice } from '@reduxjs/toolkit';
import { LIST_REQUEST, LIST_SUCCESS, LIST_FAIL, LIST_RESET, COMPANY_REQUEST, COMPANY_FAIL, COMPANY_SUCCESS } from '../types/users';

export const usersReducer = (state = { USERLIST: [] }, action) => {
  switch (action.type) {
    case LIST_REQUEST:
      return {
        loading: true,
        USERLIST: [],
      };

    case LIST_SUCCESS:
      return {
        loading: false,
        success: true,
        USERLIST: action.payload,
      };

    case LIST_FAIL:
      console.log(action.payload);
      return {
        loading: false,
        error: action.payload,
        USERLIST: [],
      };

    case LIST_RESET:
      return {
        USERLIST: [],
      };

    default:
      return state;
  }
};

// export const companyReducer = (state = {}, action) => {
//   switch (action.type) {
//     case COMPANY_REQUEST:
//       return {
//         loading: true,
//       };

//     case COMPANY_SUCCESS:
//       console.log(state)
//       return {
//         loading: false,
//         success: true,
//       };

//     case COMPANY_FAIL:
//       return {
//         loading: false,
//         error: action.payload,
//       };

//     default:
//       return state;
//   }
// }

export const companyReducer = createSlice({
  name: 'company',
  initialState: {
    loading: false,
    success: false,
    error: null,
    company: {}
  },
  reducers: {
    companyRequest: (state, action) => {
      state.loading = true;
    },
    companySuccess: (state, action) => {
      state.loading = false;
      state.success = true;
      state.company = action.payload;
    },
    companyFail: (state, action) => {
      state.error = action.payload;
      state.loading = false;
    }
  }
})


