import axios from 'axios';
import FileSaver from 'file-saver';
import { createSlice } from '@reduxjs/toolkit';
import { DOMAIN } from '../constants';
import { logout, login } from './authActions';

export const userSlice = createSlice({
  name: 'user',
  initialState: {
    clientsInfo: {
      loading: false,
      error: null,
      CLIENTLIST: [],
      count: 0,
      forSale: {
        current: 0,
        total: 0,
      },
      recentlySold: {
        current: 0,
        total: 0,
      },
      highestPage: 0,
      deleted: 0,
      message: null,
    },
    usersInfo: {
      loading: false,
      error: null,
      USERLIST: [],
    },
    recentlySoldInfo: {
      loading: false,
      error: null,
      RECENTLYSOLDLIST: [],
      recentlySoldFilters: [],
      highestPage: 0,
      count: 0,
    },
    forSaleInfo: {
      loading: false,
      error: null,
      FORSALELIST: [],
      forSaleFilters: [],
      highestPage: 0,
      count: 0,
    },
    referralInfo: {
      loading: false,
      error: null,
      REFERRALLIST: [],
      highestPage: 0,
    },
    saveFilter: {
      success: false,
      error: null,
    },
  },
  reducers: {
    // -----------------  CLIENTS  -----------------
    clients: (state, action) => {
      state.clientsInfo.CLIENTLIST = action.payload.results.clients;
      state.clientsInfo.count = action.payload.count;
      state.clientsInfo.forSale.current = action.payload.results.forSale;
      state.clientsInfo.forSale.total = action.payload.results.forSaleAllTime;
      state.clientsInfo.recentlySold.current = action.payload.results.recentlySold;
      state.clientsInfo.recentlySold.total = action.payload.results.recentlySoldAllTime;
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
      state.clientsInfo.done = false;
    },
    moreClients: (state, action) => {
      state.clientsInfo.CLIENTLIST = [...state.clientsInfo.CLIENTLIST, ...action.payload.results.clients];
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
    },

    newPage: (state, action) => {
      state.clientsInfo.highestPage = action.payload;
    },
    clientsError: (state, action) => {
      state.clientsInfo.error = action.payload;
      state.clientsInfo.loading = false;
      state.clientsInfo.CLIENTLIST = [];
    },
    clientsLoading: (state) => {
      state.clientsInfo.loading = true;
    },
    clientsNotLoading: (state) => {
      state.clientsInfo.loading = false;
    },
    clientsNotAdded: (state, action) => {
      state.clientsInfo.deleted = action.payload;
    },
    clientsUpload: (state, action) => {
      state.clientsInfo.message = action.payload;
    },

    // -----------------  USERS  -----------------
    users: (state, action) => {
      state.usersInfo.USERLIST = action.payload;
      state.usersInfo.loading = false;
      state.usersInfo.error = null;
    },
    usersError: (state, action) => {
      state.usersInfo.error = action.payload;
      state.usersInfo.loading = false;
      state.usersInfo.USERLIST = [];
    },
    usersLoading: (state) => {
      state.usersInfo.loading = true;
      state.usersInfo.USERLIST = [];
    },

    // -----------------  RECENTLY SOLD  -----------------
    recentlySold: (state, action) => {
      state.recentlySoldInfo.RECENTLYSOLDLIST = action.payload.results.data;
      state.recentlySoldInfo.loading = false;
      state.recentlySoldInfo.error = null;
      state.recentlySoldInfo.count = action.payload.count;
      state.recentlySoldInfo.recentlySoldFilters = action.payload.results.savedFilters;
    },
    recentlySoldError: (state, action) => {
      state.recentlySoldInfo.error = action.payload;
      state.recentlySoldInfo.loading = false;
      state.recentlySoldInfo.RECENTLYSOLDLIST = [];
    },
    recentlySoldLoading: (state) => {
      state.recentlySoldInfo.loading = true;
      state.recentlySoldInfo.RECENTLYSOLDLIST = [];
      state.recentlySoldInfo.highestPage = 0;
    },
    moreRecentlySold: (state, action) => {
      state.recentlySoldInfo.RECENTLYSOLDLIST = [
        ...state.recentlySoldInfo.RECENTLYSOLDLIST,
        ...action.payload.results.data,
      ];
      state.recentlySoldInfo.loading = false;
      state.recentlySoldInfo.error = null;
      state.recentlySoldInfo.count = action.payload.count;
    },

    newRecentlySoldPage: (state, action) => {
      state.recentlySoldInfo.highestPage = action.payload;
    },

    // -----------------  FOR SALE  -----------------
    forSale: (state, action) => {
      state.forSaleInfo.FORSALELIST = action.payload.results.data;
      state.forSaleInfo.loading = false;
      state.forSaleInfo.error = null;
      state.forSaleInfo.count = action.payload.count;
      state.forSaleInfo.forSaleFilters = action.payload.results.savedFilters;
    },
    forSaleError: (state, action) => {
      state.forSaleInfo.error = action.payload;
      state.forSaleInfo.loading = false;
      state.forSaleInfo.FORSALELIST = [];
    },
    forSaleLoading: (state) => {
      state.forSaleInfo.loading = true;
      state.forSaleInfo.FORSALELIST = [];
      state.forSaleInfo.highestPage = 0;
    },
    moreForSale: (state, action) => {
      state.forSaleInfo.FORSALELIST = [...state.forSaleInfo.FORSALELIST, ...action.payload.results.data];
      state.forSaleInfo.loading = false;
      state.forSaleInfo.error = null;
      state.forSaleInfo.count = action.payload.count;
    },

    newForSalePage: (state, action) => {
      state.forSaleInfo.highestPage = action.payload;
    },

    // -----------------  REFERRALS  -----------------
    referrals: (state, action) => {
      state.referralInfo.REFERRALLIST = action.payload;
      state.referralInfo.loading = false;
      state.referralInfo.error = null;
    },
    referralsError: (state, action) => {
      state.referralInfo.error = action.payload;
      state.referralInfo.loading = false;
      state.referralInfo.REFERRALLIST = [];
    },
    referralsLoading: (state) => {
      state.referralInfo.loading = true;
    },
    moreReferrals: (state, action) => {
      state.referralInfo.REFERRALLIST = [...state.referralInfo.REFERRALLIST, ...action.payload];
      state.referralInfo.loading = false;
      state.referralInfo.error = null;
    },
    newReferralsPage: (state, action) => {
      state.referralInfo.highestPage = action.payload;
    },
    logoutClients: (state) => {
      state.clientsInfo.CLIENTLIST = [];
      state.clientsInfo.count = 0;
      state.clientsInfo.forSale.current = 0;
      state.clientsInfo.forSale.total = 0;
      state.clientsInfo.recentlySold.current = 0;
      state.clientsInfo.recentlySold.total = 0;
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
      state.clientsInfo.done = false;
      state.clientsInfo.highestPage = 0;
      state.clientsInfo.deleted = 0;
      state.clientsInfo.message = null;
      state.usersInfo.USERLIST = [];
      state.usersInfo.loading = false;
      state.usersInfo.error = null;
      state.forSaleInfo.FORSALELIST = [];
      state.forSaleInfo.loading = false;
      state.forSaleInfo.error = null;
      state.forSaleInfo.count = 0;
      state.forSaleInfo.highestPage = 0;
      state.recentlySoldInfo.RECENTLYSOLDLIST = [];
      state.recentlySoldInfo.loading = false;
      state.recentlySoldInfo.error = null;
      state.recentlySoldInfo.count = 0;
      state.recentlySoldInfo.highestPage = 0;
      state.referralInfo.REFERRALLIST = [];
      state.referralInfo.loading = false;
      state.referralInfo.error = null;
      state.referralInfo.highestPage = 0;
    },

    saveFilter: (state) => {
      state.saveFilter.success = true;
    },
    saveFilterLoading: (state) => {
      state.saveFilter.success = false;
    },
    saveFilterError: (state, action) => {
      state.saveFilter.error = action.payload;
      state.saveFilter.success = false;
    },
  },
});

export const {
  clientsNotAdded,
  clients,
  moreClients,
  newPage,
  clientsUpload,
  clientsLoading,
  clientsNotLoading,
  clientsError,
  users,
  usersLoading,
  usersError,
  recentlySold,
  recentlySoldLoading,
  recentlySoldError,
  newRecentlySoldPage,
  moreRecentlySold,
  forSale,
  forSaleLoading,
  forSaleError,
  newForSalePage,
  moreForSale,
  referrals,
  referralsLoading,
  referralsError,
  moreReferrals,
  newReferralsPage,
  logoutClients,
  saveFilter,
  saveFilterLoading,
  saveFilterError,
} = userSlice.actions;
export const selectClients = (state) => state.user.clientsInfo;
export const selectRecentlySold = (state) => state.user.recentlySoldInfo;
export const selectForSale = (state) => state.user.forSaleInfo;
export const selectUsers = (state) => state.user.usersInfo;
export const selectReferrals = (state) => state.user.referralInfo;
export const saveFilterSuccess = (state) => state.user.saveFilter.success;
export default userSlice.reducer;

// eslint-disable-next-line arrow-body-style
export const getRefreshToken = (dispatch, func) => {
  return async (dispatch, getState) => {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
      },
    };
    const data = { refresh: userInfo.refresh };
    try {
      const response = await axios.post(`${DOMAIN}/api/v1/accounts/refresh/`, data, config);
      const newUserInfo = {
        ...userInfo,
        refresh: response.data.refresh,
        accessToken: response.data.access,
      };
      dispatch(login(newUserInfo));
      dispatch(func);
    } catch (error) {
      console.log('error', error);
      dispatch(logout());
    }
  };
};

export const usersAsync = () => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    dispatch(usersLoading());
    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/users/${userInfo.company.id}`, config);
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, usersAsync()));
    } else {
      dispatch(logout());
    }
  }
};

export const deleteUserAsync = (ids) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const { id: company } = userInfo.company;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
      data: JSON.stringify(ids),
    };
    dispatch(usersLoading());
    const { data } = await axios.delete(`${DOMAIN}/api/v1/accounts/manageuser/${company}/`, config);
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, deleteUserAsync(ids)));
    }
  }
};

export const clientsAsync =
  (page, refreshed = false) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };

      if (page === 1) {
        dispatch(clientsLoading());
      }
      if (page > reduxStore.user.clientsInfo.highestPage || page === 1) {
        const { data } = await axios.get(`${DOMAIN}/api/v1/data/clients/${userInfo.id}?page=${page}`, config);
        if (page === 1) {
          dispatch(clients(data));
        } else {
          dispatch(moreClients(data));
        }
        if (data.results.clients.length > 0) {
          dispatch(newPage(page));
          if (data.results.clients.length === 1000) {
            dispatch(clientsAsync(page + 1));
          }
        }
      } else {
        dispatch(clientsNotLoading());
      }
    } catch (error) {
      // localStorage.removeItem('userInfo');
      // dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));

      if (error.response.status === 403 && !refreshed) {
        dispatch(getRefreshToken(dispatch, clientsAsync(page, true)));
      } else {
        dispatch(logout());
      }
    }
  };

export const deleteClientAsync = (ids) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    dispatch(clientsLoading());
    const chunkSize = 1000;
    let i = 0;
    for (i; i < ids.length; i += chunkSize) {
      const chunk = ids.slice(i, i + chunkSize);

      await axios.put(`${DOMAIN}/api/v1/data/updateclient/`, { clients: chunk, type: 'delete' }, config);
    }
    const chunk = ids.slice(i, i + chunkSize);
    if (chunk.length > 0) {
      await axios.put(`${DOMAIN}/api/v1/data/updateclient/`, { clients: chunk, type: 'delete' }, config);
    }
    dispatch(clientsAsync(1));
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, deleteClientAsync(ids)));
    }
  }
};

export const updateClientAsync =
  (id, contacted, note, errorFlag, latitude, longitude) => async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };
      dispatch(clientsLoading());
      await axios.put(
        `${DOMAIN}/api/v1/data/updateclient/`,
        { clients: id, type: 'edit', contacted, note, errorFlag, latitude, longitude },
        config
      );
      dispatch(clientsAsync(1));
    } catch (error) {
      dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
      if (error.response.status === 403) {
        dispatch(getRefreshToken(dispatch, updateClientAsync(id, contacted, note, errorFlag, latitude, longitude)));
      }
    }
  };

export const uploadClientsUpdateAsync = (id) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    const { data } = await axios.get(`${DOMAIN}/api/v1/data/upload/${id}/`, config);
    if (data.status === 'SUCCESS') {
      dispatch(clientsUpload(data.data));
      dispatch(clientsNotAdded(data.deleted));
      dispatch(clientsAsync(1));
    } else {
      setTimeout(() => {
        dispatch(uploadClientsUpdateAsync(id));
      }, 1000);
    }
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, uploadClientsUpdateAsync(id)));
    }
  }
};

export const uploadClientsAsync = (customers) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const { id: company } = userInfo.company;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };

    dispatch(clientsLoading());
    const { data } = await axios.put(`${DOMAIN}/api/v1/data/upload/${company}/`, customers, config);
    dispatch(clientsUpload(data.data));
    dispatch(uploadClientsUpdateAsync(data.task));
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, uploadClientsAsync(customers)));
    }
  }
};

export const filterClientsAsync =
  (
    statusFilters,
    minPrice,
    maxPrice,
    minYear,
    maxYear,
    tagFilters,
    equipInstallDateMin,
    equipInstallDateMax,
    city,
    state,
    zipCode,
    customerSinceMin,
    customerSinceMax
  ) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };
      let filters = '';
      if (statusFilters.length > 0) {
        filters += `&status=${statusFilters.join(',')}`;
      }
      if (minPrice) {
        filters += `&min_price=${minPrice}`;
      }
      if (maxPrice) {
        filters += `&max_price=${maxPrice}`;
      }
      if (minYear) {
        filters += `&min_year=${minYear}`;
      }
      if (maxYear) {
        filters += `&max_year=${maxYear}`;
      }
      if (tagFilters.length > 0) {
        filters += `&tags=${tagFilters.join('&tags=')}`;
      }
      if (equipInstallDateMin) {
        filters += `&equip_install_date_min=${equipInstallDateMin}`;
      }
      if (equipInstallDateMax) {
        filters += `&equip_install_date_max=${equipInstallDateMax}`;
      }
      if (city) {
        filters += `&city=${city}`;
      }
      if (state) {
        filters += `&state=${state}`;
      }
      if (zipCode) {
        filters += `&zip_code=${zipCode}`;
      }
      if (customerSinceMin) {
        filters += `&customer_since_min=${customerSinceMin}`;
      }
      if (customerSinceMax) {
        filters += `&customer_since_max=${customerSinceMax}`;
      }
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/clients/${userInfo.id}/?page=1${filters}`, config);
      dispatch(clients(data));
    } catch (error) {
      dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
      if (error.response.status === 403) {
        dispatch(
          getRefreshToken(
            dispatch,
            filterClientsAsync(
              statusFilters,
              minPrice,
              maxPrice,
              minYear,
              maxYear,
              tagFilters,
              equipInstallDateMin,
              equipInstallDateMax,
              city,
              state,
              zipCode,
              customerSinceMin,
              customerSinceMax
            )
          )
        );
      }
    }
  };

export const serviceTitanUpdateAsync = (id) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };

    const { data } = await axios.get(`${DOMAIN}/api/v1/data/servicetitan/${id}/`, config);
    if (data.status === 'SUCCESS') {
      dispatch(clientsNotAdded(data.deleted));
      dispatch(clientsUpload(data.data));
      dispatch(clientsAsync(1));
    } else {
      setTimeout(() => {
        dispatch(serviceTitanUpdateAsync(id));
      }, 1000);
    }
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, serviceTitanUpdateAsync(id)));
    }
  }
};

export const serviceTitanSync = (option) => async (dispatch, getState) => {
  try {
    dispatch(clientsLoading());
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const { id: company } = userInfo.company;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    const { data } = await axios.put(`${DOMAIN}/api/v1/data/servicetitan/${company}/`, { option }, config);
    dispatch(serviceTitanUpdateAsync(data.task));
  } catch (error) {
    throw new Error(error);
    // dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const salesForceSync = () => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const { id: company } = userInfo.company;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    // dispatch(clientsLoading());
    await axios.put(`${DOMAIN}/api/v1/data/salesforce/${company}/`, config);
    dispatch(clientsAsync(1));
  } catch (error) {
    throw new Error(error);
    // dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

// export const createCompany = (company, email) => async () => {
//   try {

//     const reduxStore = getState();
//     const {userInfo} = reduxStore.auth.userInfo;
//     const config = {
//       headers: {
//         'Content-type': 'application/json',
//         Authorization: `Bearer ${userInfo.access_token}`,
//       },
//     };

//     await axios.post(
//       `${DOMAIN}/api/v1/accounts/createCompany/`,
//       { 'name': company, email},
//       config
//     );

//   } catch (error) {
//     throw new Error(error);
//   }
// };

export const addUser = (email) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };

    dispatch(usersLoading());
    const { data } = await axios.post(
      `${DOMAIN}/api/v1/accounts/manageuser/${userInfo.company.id}/`,
      { email },
      config
    );
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, addUser(email)));
    }
  }
};

export const makeAdminAsync = (userId) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };

    dispatch(usersLoading());
    const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/manageuser/${userId}/`, {}, config);
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    // if (error.response.status === 403) {
    //   dispatch(getRefreshToken(dispatch, makeAdminAsync(userId)));
    // }
  }
};

export const update = () => async (getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    await axios.get(`${DOMAIN}/api/v1/data/update/${userInfo.company.id}`, config);
  } catch (error) {
    throw new Error(error);
  }
};

export const forSaleAsync = (page) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    if (page === 1) {
      dispatch(forSaleLoading());
    }
    if (page > reduxStore.user.forSaleInfo.highestPage) {
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/forsale/${userInfo.company.id}?page=${page}`, config);
      if (data.results.data.length > 0) {
        dispatch(newForSalePage(page));
        if (data.results.data.length === 1000) {
          dispatch(forSaleAsync(page + 1));
        }
      }
      if (page === 1) {
        dispatch(forSale(data));
      } else {
        dispatch(moreForSale(data));
      }
    }
  } catch (error) {
    dispatch(forSaleError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, forSaleAsync(page)));
    }
  }
};

export const filterForSaleAsync =
  (minPrice, maxPrice, minYear, maxYear, minDaysAgo, maxDaysAgo, tagFilters, city, state, zipCode, savedFilter) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };
      dispatch(forSaleLoading());
      let filters = '';
      if (minPrice) {
        filters += `&min_price=${minPrice}`;
      }
      if (maxPrice) {
        filters += `&max_price=${maxPrice}`;
      }
      if (minYear) {
        filters += `&min_year=${minYear}`;
      }
      if (maxYear) {
        filters += `&max_year=${maxYear}`;
      }
      if (minDaysAgo) {
        filters += `&min_days_ago=${minDaysAgo}`;
      }
      if (maxDaysAgo) {
        filters += `&max_days_ago=${maxDaysAgo}`;
      }
      if (tagFilters) {
        filters += `&tags=${tagFilters.join(',')}`;
      }
      if (city) {
        filters += `&city=${city}`;
      }
      if (state) {
        filters += `&state=${state}`;
      }
      if (zipCode) {
        filters += `&zip_code=${zipCode}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      const { data } = await axios.get(
        `${DOMAIN}/api/v1/data/forsale/${userInfo.company.id}/?page=1${filters}`,
        config
      );
      dispatch(forSale(data));
    } catch (error) {
      dispatch(forSaleError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
      if (error.response.status === 403) {
        dispatch(
          getRefreshToken(
            dispatch,
            filterForSaleAsync(
              minPrice,
              maxPrice,
              minYear,
              maxYear,
              minDaysAgo,
              maxDaysAgo,
              tagFilters,
              city,
              state,
              zipCode,
              savedFilter
            )
          )
        );
      }
    }
  };

export const recentlySoldAsync = (page) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    if (page === 1) {
      dispatch(recentlySoldLoading());
    }
    if (page > reduxStore.user.recentlySoldInfo.highestPage) {
      const { data } = await axios.get(
        `${DOMAIN}/api/v1/data/recentlysold/${userInfo.company.id}?page=${page}`,
        config
      );
      if (data.results.data.length > 0) {
        dispatch(newRecentlySoldPage(page));
        if (data.results.data.length === 1000) {
          dispatch(recentlySoldAsync(page + 1));
        }
      }
      if (page === 1) {
        dispatch(recentlySold(data));
      } else {
        dispatch(moreRecentlySold(data));
      }
    }
  } catch (error) {
    dispatch(
      recentlySoldError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
    );
    if (error.response.status === 403) {
      dispatch(getRefreshToken(dispatch, recentlySoldAsync(page)));
    }
  }
};

export const filterRecentlySoldAsync =
  (minPrice, maxPrice, minYear, maxYear, minDaysAgo, maxDaysAgo, tagFilters, city, state, zipCode, savedFilter) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };
      dispatch(recentlySoldLoading());
      let filters = '';
      if (minPrice) {
        filters += `&min_price=${minPrice}`;
      }
      if (maxPrice) {
        filters += `&max_price=${maxPrice}`;
      }
      if (minYear) {
        filters += `&min_year=${minYear}`;
      }
      if (maxYear) {
        filters += `&max_year=${maxYear}`;
      }
      if (minDaysAgo) {
        filters += `&min_days_ago=${minDaysAgo}`;
      }
      if (maxDaysAgo) {
        filters += `&max_days_ago=${maxDaysAgo}`;
      }
      if (tagFilters) {
        filters += `&tags=${tagFilters.join(',')}`;
      }
      if (city) {
        filters += `&city=${city}`;
      }
      if (state) {
        filters += `&state=${state}`;
      }
      if (zipCode) {
        filters += `&zip_code=${zipCode}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      const { data } = await axios.get(
        `${DOMAIN}/api/v1/data/recentlysold/${userInfo.company.id}/?page=1${filters}`,
        config
      );
      dispatch(recentlySold(data));
    } catch (error) {
      dispatch(
        recentlySoldError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
      );
      if (error.response.status === 403) {
        dispatch(
          getRefreshToken(
            dispatch,
            filterRecentlySoldAsync(
              minPrice,
              maxPrice,
              minYear,
              maxYear,
              minDaysAgo,
              maxDaysAgo,
              tagFilters,
              city,
              state,
              zipCode,
              savedFilter
            )
          )
        );
      }
    }
  };

export const makeReferralAsync = (id, area) => async (getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    await axios.post(`${DOMAIN}/api/v1/accounts/referrals/${userInfo.company.id}/`, { id, area }, config);
  } catch (error) {
    throw new Error(error);
  }
};

export const referralsAsync = (page) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    if (page === 1) {
      dispatch(referralsLoading());
    }
    if (page > reduxStore.user.referralInfo.highestPage) {
      const { data } = await axios.get(
        `${DOMAIN}/api/v1/accounts/referrals/${userInfo.company.id}?page=${page}`,
        config
      );
      if (data.results.length > 0) {
        dispatch(newReferralsPage(page));
      }
      if (page === 1) {
        dispatch(referrals(data));
      } else {
        dispatch(moreReferrals(data));
      }
    }
  } catch (error) {
    console.log('error', error);
    dispatch(referralsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const getClientsCSV = (
  statusFilters,
  minPrice,
  maxPrice,
  minYear,
  maxYear,
  tagFilters,
  equipInstallDateMin,
  equipInstallDateMax,
  city,
  state,
  zipCode,
  customerSinceMin,
  customerSinceMax
  // eslint-disable-next-line arrow-body-style
) => {
  return async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
        responseType: 'blob', // Tell axios to expect a binary response
      };
      let filters = '';
      if (statusFilters.length > 0) {
        filters += `&status=${statusFilters.join(',')}`;
      }
      if (minPrice) {
        filters += `&min_price=${minPrice}`;
      }
      if (maxPrice) {
        filters += `&max_price=${maxPrice}`;
      }
      if (minYear) {
        filters += `&min_year=${minYear}`;
      }
      if (maxYear) {
        filters += `&max_year=${maxYear}`;
      }
      if (tagFilters.length > 0) {
        filters += `&tags=${tagFilters.join('&tags=')}`;
      }
      if (equipInstallDateMin) {
        filters += `&equip_install_date_min=${equipInstallDateMin}`;
      }
      if (equipInstallDateMax) {
        filters += `&equip_install_date_max=${equipInstallDateMax}`;
      }
      if (city) {
        filters += `&city=${city}`;
      }
      if (state) {
        filters += `&state=${state}`;
      }
      if (zipCode) {
        filters += `&zip_code=${zipCode}`;
      }
      if (customerSinceMin) {
        filters += `&customer_since_min=${customerSinceMin}`;
      }
      if (customerSinceMax) {
        filters += `&customer_since_max=${customerSinceMax}`;
      }
      const response = await axios.get(`${DOMAIN}/api/v1/data/downloadclients/${userInfo.id}/?${filters}`, config);
      const csvBlob = new Blob([response.data], { type: 'text/csv' }); // Convert binary response to a blob
      FileSaver.saveAs(csvBlob, 'clients.csv'); // Download the file using FileSaver
    } catch (error) {
      console.log(error);
    }
  };
};

export const getRecentlySoldCSV =
  (minPrice, maxPrice, minYear, maxYear, minDaysAgo, maxDaysAgo, tagFilters, city, state, zipCode, savedFilter) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
        responseType: 'blob', // Tell axios to expect a binary response
      };
      let filters = '';
      if (minPrice) {
        filters += `&min_price=${minPrice}`;
      }
      if (maxPrice) {
        filters += `&max_price=${maxPrice}`;
      }
      if (minYear) {
        filters += `&min_year=${minYear}`;
      }
      if (maxYear) {
        filters += `&max_year=${maxYear}`;
      }
      if (minDaysAgo) {
        filters += `&min_days_ago=${minDaysAgo}`;
      }
      if (maxDaysAgo) {
        filters += `&max_days_ago=${maxDaysAgo}`;
      }
      if (tagFilters) {
        filters += `&tags=${tagFilters.join(',')}`;
      }
      if (city) {
        filters += `&city=${city}`;
      }
      if (state) {
        filters += `&state=${state}`;
      }
      if (zipCode) {
        filters += `&zip_code=${zipCode}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      const response = await axios.get(
        `${DOMAIN}/api/v1/data/downloadrecentlysold/${userInfo.company.id}/?${filters}`,
        config
      );
      const csvBlob = new Blob([response.data], { type: 'text/csv' }); // Convert binary response to a blob
      FileSaver.saveAs(csvBlob, 'homelistings.csv'); // Download the file using FileSaver
    } catch (error) {
      console.log(error);
    }
  };

export const getForSaleCSV =
  (minPrice, maxPrice, minYear, maxYear, minDaysAgo, maxDaysAgo, tagFilters, city, state, zipCode, savedFilter) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
        responseType: 'blob', // Tell axios to expect a binary response
      };
      console.log(3);
      let filters = '';
      if (minPrice) {
        filters += `&min_price=${minPrice}`;
      }
      if (maxPrice) {
        filters += `&max_price=${maxPrice}`;
      }
      if (minYear) {
        filters += `&min_year=${minYear}`;
      }
      if (maxYear) {
        filters += `&max_year=${maxYear}`;
      }
      if (minDaysAgo) {
        filters += `&min_days_ago=${minDaysAgo}`;
      }
      if (maxDaysAgo) {
        filters += `&max_days_ago=${maxDaysAgo}`;
      }
      if (tagFilters) {
        filters += `&tags=${tagFilters.join(',')}`;
      }
      if (city) {
        filters += `&city=${city}`;
      }
      if (state) {
        filters += `&state=${state}`;
      }
      if (zipCode) {
        filters += `&zip_code=${zipCode}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      const response = await axios.get(
        `${DOMAIN}/api/v1/data/downloadforsale/${userInfo.company.id}/?${filters}`,
        config
      );
      const csvBlob = new Blob([response.data], { type: 'text/csv' }); // Convert binary response to a blob
      FileSaver.saveAs(csvBlob, 'forsale.csv'); // Download the file using FileSaver
    } catch (error) {
      console.log(error);
    }
  };

export const saveRecentlySoldFilterAsync =
  (
    filterName,
    minPrice,
    maxPrice,
    minYear,
    maxYear,
    minDaysAgo,
    maxDaysAgo,
    tagFilters,
    city,
    state,
    zipCode,
    forZapier
  ) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };
      const body = {
        filter_name: filterName,
        min_price: minPrice,
        max_price: maxPrice,
        min_year: minYear,
        max_year: maxYear,
        min_days_ago: minDaysAgo,
        max_days_ago: maxDaysAgo,
        tag_filters: tagFilters,
        city,
        state,
        zip_code: zipCode,
        for_zapier: forZapier,
      };
      dispatch(saveFilterLoading());
      await axios.post(`${DOMAIN}/api/v1/data/recentlysold/${userInfo.company.id}/`, body, config);
      dispatch(saveFilter());
    } catch (error) {
      dispatch(
        saveFilterError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
      );
    }
  };

export const saveForSaleFilterAsync =
  (
    filterName,
    minPrice,
    maxPrice,
    minYear,
    maxYear,
    minDaysAgo,
    maxDaysAgo,
    tagFilters,
    city,
    state,
    zipCode,
    forZapier
  ) =>
  async (dispatch, getState) => {
    try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };
      const body = {
        filter_name: filterName,
        min_price: minPrice,
        max_price: maxPrice,
        min_year: minYear,
        max_year: maxYear,
        min_days_ago: minDaysAgo,
        max_days_ago: maxDaysAgo,
        tag_filters: tagFilters,
        city,
        state,
        zip_code: zipCode,
        for_zapier: forZapier,
      };
      dispatch(saveFilterLoading());
      await axios.post(`${DOMAIN}/api/v1/data/forsale/${userInfo.company.id}/`, body, config);
      dispatch(saveFilter());
    } catch (error) {
      dispatch(
        saveFilterError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
      );
    }
  };
