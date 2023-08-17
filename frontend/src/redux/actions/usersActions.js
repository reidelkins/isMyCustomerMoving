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
      NEWADDRESSLIST: [],
      customerDataFilters: [],
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
    dashboardData: {
      loading: false,
      error: null,
      totalRevenue: 0,
      revenueByMonth: {},
      forSaleByMonth: {},
      recentlySoldByMonth: {},
      customerRetention: {},
      monthsActive: 0,
      clientsAcquired: 0,
      clientsAcquiredByMonth: {},
      retrieved: false,
    }
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
      state.clientsInfo.customerDataFilters = action.payload.results.savedFilters;
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
      state.clientsInfo.done = false;
    },
    moreClients: (state, action) => {
      state.clientsInfo.CLIENTLIST = [...state.clientsInfo.CLIENTLIST, ...action.payload.results.clients];
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
    },
    newAddress: (state, action) => {
      state.clientsInfo.NEWADDRESSLIST = action.payload.clients;
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

    // -----------------  Company Dashboard  -----------------
    companyDashboard: (state, action) => {
      state.dashboardData.totalRevenue = action.payload.totalRevenue;
      state.dashboardData.revenueByMonth = action.payload.revenueByMonth;
      state.dashboardData.forSaleByMonth = action.payload.forSaleByMonth;
      state.dashboardData.recentlySoldByMonth = action.payload.recentlySoldByMonth;
      state.dashboardData.monthsActive = action.payload.monthsActive;
      state.dashboardData.customerRetention = action.payload.customerRetention;
      state.dashboardData.clientsAcquired = action.payload.clientsAcquired;
      state.dashboardData.clientsAcquiredByMonth = action.payload.clientsAcquiredByMonth;
      state.dashboardData.loading = false;
      state.dashboardData.error = null;
      state.dashboardData.retrieved = true;
    },
    companyDashboardError: (state, action) => {
      state.dashboardData.error = action.payload;
      state.dashboardData.loading = false;
      state.dashboardData.retrieved = false;
    },
    companyDashboardLoading: (state) => {
      state.dashboardData.loading = true;
      state.dashboardData.retrieved = false;
    },

    // -----------------  SAVE FILTER  -----------------
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

    // -----------------  LOGOUT  -----------------
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
  newAddress,
  companyDashboard,
  companyDashboardLoading,
  companyDashboardError,
} = userSlice.actions;
export const selectClients = (state) => state.user.clientsInfo;
export const selectRecentlySold = (state) => state.user.recentlySoldInfo;
export const selectForSale = (state) => state.user.forSaleInfo;
export const selectUsers = (state) => state.user.usersInfo;
export const selectReferrals = (state) => state.user.referralInfo;
export const saveFilterSuccess = (state) => state.user.saveFilter.success;
export const companyDashboardData = (state) => state.user.dashboardData;
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

export const updateCounts = (contacted, status, updatedClients) => async (dispatch, getState) => {
  const reduxStore = getState();    
  const data = {
    count: reduxStore.user.clientsInfo.count,
    results: {
      clients : updatedClients,
      forSale: status !== "House For Sale"
        ? reduxStore.user.clientsInfo.forSale.current
        : reduxStore.user.clientsInfo.forSale.current + (contacted ? -1 : 1),
      forSaleAllTime: reduxStore.user.clientsInfo.forSale.total,
      recentlySold: status !== "House Recently Sold (6)"
        ? reduxStore.user.clientsInfo.recentlySold.current 
        : reduxStore.user.clientsInfo.recentlySold.current + (contacted ? -1 : 1),
      recentlySoldAllTime: reduxStore.user.clientsInfo.recentlySold.total,
      savedFilters: reduxStore.user.clientsInfo.customerDataFilters,
    }
    
    
    
  }
  dispatch(clients(data));  

  }

export const usersAsync = (refreshed = false) => async (dispatch, getState) => {
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
    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/users/`, config);
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, usersAsync(true)));
    } else {
      dispatch(logout());
    }
  }
};

export const deleteUserAsync = (ids, refreshed = false) => async (dispatch, getState) => {
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
    const { data } = await axios.put(`${DOMAIN}/api/v1/accounts/manageuser/`, { ids }, config);
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, deleteUserAsync(ids, true)));
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
      if (page === 1 && reduxStore.user.clientsInfo.highestPage === 0) {
        dispatch(clientsLoading());
      }
      if (page > reduxStore.user.clientsInfo.highestPage) {
        const { data } = await axios.get(`${DOMAIN}/api/v1/data/clients/?page=${page}`, config);
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
      console.log('error', error);
      if (error.response.status === 403 && !refreshed) {
        dispatch(getRefreshToken(dispatch, clientsAsync(page, true)));
      } else {
        dispatch(logout());
      }
    }
  };

export const newAddressAsync = (page, refreshed = false) => async (dispatch, getState) => {
  try {
      const reduxStore = getState();
      const { userInfo } = reduxStore.auth.userInfo;
      const config = {
        headers: {
          'Content-type': 'application/json',
          Authorization: `Bearer ${userInfo.access_token}`,
        },
      };
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/clients/?newAddress=True&page=${page}`, config);
      console.log(data)
      dispatch(newAddress(data));

    } catch (error) {
      console.log('error', error);
      if (error.response.status === 403 && !refreshed) {
        dispatch(getRefreshToken(dispatch, newAddressAsync(page, true)));
      } else {
        dispatch(logout());
      }
    }
  };

export const deleteClientAsync = (ids, refreshed = false) => async (dispatch, getState) => {
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
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, deleteClientAsync(ids, true)));
    }
  }
};

export const updateClientAsync =
  (id, contacted, note, errorFlag, latitude, longitude, refreshed = false) => async (dispatch, getState) => {
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
      if (error.response.status === 403 && !refreshed) {
        dispatch(getRefreshToken(dispatch, updateClientAsync(id, contacted, note, errorFlag, latitude, longitude, true)));
      }
    }
  };

export const uploadClientsUpdateAsync = (id, refreshed = false) => async (dispatch, getState) => {
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
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, uploadClientsUpdateAsync(id, true)));
    }
  }
};

export const uploadClientsAsync = (customers, refreshed = false) => async (dispatch, getState) => {
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
    const { data } = await axios.put(`${DOMAIN}/api/v1/data/upload/clients/`, customers, config);
    dispatch(clientsUpload(data.data));
    dispatch(uploadClientsUpdateAsync(data.task));
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, uploadClientsAsync(customers, true)));
    }
  }
};

export const uploadServiceAreasAsync = (zipCodes, refreshed = false) => async (dispatch, getState) => {
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
    const { data } = await axios.put(`${DOMAIN}/api/v1/data/upload/zips/`, zipCodes, config);    
    dispatch(login(data));
    localStorage.setItem('userInfo', JSON.stringify(data));
    window.location.reload();
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, uploadServiceAreasAsync(zipCodes, true)));
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
    customerSinceMax,
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
    savedFilter,
    uspsChanged,
    refreshed = false
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
      if (minRooms) {
        filters += `&min_beds=${minRooms}`;
      }
      if (maxRooms) {
        filters += `&max_beds=${maxRooms}`;
      }
      if (minBaths) {
        filters += `&min_baths=${minBaths}`;
      }
      if (maxBaths) {
        filters += `&max_baths=${maxBaths}`;
      }
      if (minSqft) {
        filters += `&min_sqft=${minSqft}`;
      }
      if (maxSqft) {
        filters += `&max_sqft=${maxSqft}`;
      }
      if (minLotSqft) {
        filters += `&min_lot_sqft=${minLotSqft}`;
      }
      if (maxLotSqft) {
        filters += `&max_lot_sqft=${maxLotSqft}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      if (uspsChanged) {
        filters += `&usps_changed=${uspsChanged}`;
      }
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/clients/?page=1${filters}`, config);
      dispatch(clients(data));
    } catch (error) {
      dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
      if (error.response.status === 403 && !refreshed) {
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
              customerSinceMax,
              minRooms,
              maxRooms,
              minBaths,
              maxBaths,
              minSqft,
              maxSqft,
              minLotSqft,
              maxLotSqft,
              savedFilter,
              uspsChanged,
              true
            )
          )
        );
      }
    }
  };

export const serviceTitanUpdateAsync = (id, refreshed = false) => async (dispatch, getState) => {
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
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, serviceTitanUpdateAsync(id, true)));
    }
  }
};

export const serviceTitanSync = (option, ) => async (dispatch, getState) => {
  try {
    dispatch(clientsLoading());
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    const { data } = await axios.put(`${DOMAIN}/api/v1/data/servicetitan/`, { option }, config);
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

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    // dispatch(clientsLoading());
    await axios.put(`${DOMAIN}/api/v1/data/salesforce/`, config);
    dispatch(clientsAsync(1));
  } catch (error) {
    throw new Error(error);
    // dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const addUser = (email, refreshed = false) => async (dispatch, getState) => {
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
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, addUser(email, true)));
    }
  }
};

export const makeAdminAsync = (userId, refreshed = false) => async (dispatch, getState) => {
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
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, makeAdminAsync(userId, true)));
    }
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
    await axios.get(`${DOMAIN}/api/v1/data/update/`, config);
  } catch (error) {
    throw new Error(error);
  }
};

export const forSaleAsync = (page, refreshed = false) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };

    if (page === 1 && reduxStore.user.forSaleInfo.highestPage === 0) {
        dispatch(forSaleLoading());
      }
    if (page > reduxStore.user.forSaleInfo.highestPage) {
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/forsale/?page=${page}`, config);
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
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, forSaleAsync(page, true)));
    }
  }
};

export const filterForSaleAsync =
  (
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
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
    savedFilter,
    refreshed = false
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
      if (minRooms) {
        filters += `&min_beds=${minRooms}`;
      }
      if (maxRooms) {
        filters += `&max_beds=${maxRooms}`;
      }
      if (minBaths) {
        filters += `&min_baths=${minBaths}`;
      }
      if (maxBaths) {
        filters += `&max_baths=${maxBaths}`;
      }
      if (minSqft) {
        filters += `&min_sqft=${minSqft}`;
      }
      if (maxSqft) {
        filters += `&max_sqft=${maxSqft}`;
      }
      if (minLotSqft) {
        filters += `&min_lot_sqft=${minLotSqft}`;
      }
      if (maxLotSqft) {
        filters += `&max_lot_sqft=${maxLotSqft}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/forsale/?page=1${filters}`, config);
      dispatch(forSale(data));
    } catch (error) {
      dispatch(forSaleError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
      if (error.response.status === 403 && !refreshed) {
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
              savedFilter,
              true
            )
          )
        );
      }
    }
  };

export const recentlySoldAsync = (page, refreshed = false) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    
    if (page === 1 && reduxStore.user.recentlySoldInfo.highestPage === 0) {
      dispatch(recentlySoldLoading());
    }
    if (page > reduxStore.user.recentlySoldInfo.highestPage) {
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/recentlysold/?page=${page}`, config);
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
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, recentlySoldAsync(page, true)));
    }
  }
};

export const filterRecentlySoldAsync =
  (
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
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
    savedFilter,
    refreshed = false
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
      if (minRooms) {
        filters += `&min_beds=${minRooms}`;
      }
      if (maxRooms) {
        filters += `&max_beds=${maxRooms}`;
      }
      if (minBaths) {
        filters += `&min_baths=${minBaths}`;
      }
      if (maxBaths) {
        filters += `&max_baths=${maxBaths}`;
      }
      if (minSqft) {
        filters += `&min_sqft=${minSqft}`;
      }
      if (maxSqft) {
        filters += `&max_sqft=${maxSqft}`;
      }
      if (minLotSqft) {
        filters += `&min_lot_sqft=${minLotSqft}`;
      }
      if (maxLotSqft) {
        filters += `&max_lot_sqft=${maxLotSqft}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      const { data } = await axios.get(`${DOMAIN}/api/v1/data/recentlysold/?page=1${filters}`, config);
      dispatch(recentlySold(data));
    } catch (error) {
      dispatch(
        recentlySoldError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
      );
      if (error.response.status === 403 && !refreshed) {
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
              savedFilter,
              true
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
    await axios.post(`${DOMAIN}/api/v1/accounts/referrals/`, { id, area }, config);
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
      const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/referrals/?page=${page}`, config);
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
  customerSinceMax,
  minRooms,
  maxRooms,
  minBaths,
  maxBaths,
  minSqft,
  maxSqft,
  minLotSqft,
  maxLotSqft,
  savedFilter,
  uspsChanged
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
      if (minRooms) {
        filters += `&min_beds=${minRooms}`;
      }
      if (maxRooms) {
        filters += `&max_beds=${maxRooms}`;
      }
      if (minBaths) {
        filters += `&min_baths=${minBaths}`;
      }
      if (maxBaths) {
        filters += `&max_baths=${maxBaths}`;
      }
      if (minSqft) {
        filters += `&min_sqft=${minSqft}`;
      }
      if (maxSqft) {
        filters += `&max_sqft=${maxSqft}`;
      }
      if (minLotSqft) {
        filters += `&min_lot_sqft=${minLotSqft}`;
      }
      if (maxLotSqft) {
        filters += `&max_lot_sqft=${maxLotSqft}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      if (uspsChanged) {
        filters += `&usps_changed=${uspsChanged}`;
      }
      const response = await axios.get(`${DOMAIN}/api/v1/data/downloadclients/?${filters}`, config);
      const csvBlob = new Blob([response.data], { type: 'text/csv' }); // Convert binary response to a blob
      FileSaver.saveAs(csvBlob, 'clients.csv'); // Download the file using FileSaver
    } catch (error) {
      console.log(error);
    }
  };
};

export const getRecentlySoldCSV =
  (
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
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
    savedFilter
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
      if (minRooms) {
        filters += `&min_beds=${minRooms}`;
      }
      if (maxRooms) {
        filters += `&max_beds=${maxRooms}`;
      }
      if (minBaths) {
        filters += `&min_baths=${minBaths}`;
      }
      if (maxBaths) {
        filters += `&max_baths=${maxBaths}`;
      }
      if (minSqft) {
        filters += `&min_sqft=${minSqft}`;
      }
      if (maxSqft) {
        filters += `&max_sqft=${maxSqft}`;
      }
      if (minLotSqft) {
        filters += `&min_lot_sqft=${minLotSqft}`;
      }
      if (maxLotSqft) {
        filters += `&max_lot_sqft=${maxLotSqft}`;
      }
      if (savedFilter) {
        filters += `&saved_filter=${savedFilter}`;
      }
      const response = await axios.get(`${DOMAIN}/api/v1/data/downloadrecentlysold/?${filters}`, config);
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
      console.log(filters);
      console.log(`${DOMAIN}/api/v1/data/downloadforsale/?${filters}`);
      const response = await axios.get(`${DOMAIN}/api/v1/data/downloadforsale/?${filters}`, config);
      const csvBlob = new Blob([response.data], { type: 'text/csv' }); // Convert binary response to a blob
      FileSaver.saveAs(csvBlob, 'forsale.csv'); // Download the file using FileSaver
    } catch (error) {
      console.log(error);
    }
  };

export const saveCustomerDataFilterAsync =
  (
    filterName,
    minPrice,
    maxPrice,
    minYear,
    maxYear,
    equipInstallDateMin,
    equipInstallDateMax,
    tagFilters,
    city,
    state,
    zipCode,
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
    forZapier,
    customerSinceMin,
    customerSinceMax,
    statusFilters,
    uspsChanged

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
        equip_install_date_min: equipInstallDateMin,
        equip_install_date_max: equipInstallDateMax,
        tag_filters: tagFilters,
        city,
        state,
        zip_code: zipCode,
        min_beds: minRooms,
        max_beds: maxRooms,
        min_baths: minBaths,
        max_baths: maxBaths,
        min_sqft: minSqft,
        max_sqft: maxSqft,
        min_lot_sqft: minLotSqft,
        max_lot_sqft: maxLotSqft,
        for_zapier: forZapier,
        customer_since_min: customerSinceMin,
        customer_since_max: customerSinceMax,
        status_filters: statusFilters,
        usps_changed: uspsChanged
      };
      dispatch(saveFilterLoading());
      await axios.post(`${DOMAIN}/api/v1/data/clients/`, body, config);
      dispatch(saveFilter());
    } catch (error) {
      dispatch(
        saveFilterError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
      );
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
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
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
        min_beds: minRooms,
        max_beds: maxRooms,
        min_baths: minBaths,
        max_baths: maxBaths,
        min_sqft: minSqft,
        max_sqft: maxSqft,
        min_lot_sqft: minLotSqft,
        max_lot_sqft: maxLotSqft,
        for_zapier: forZapier,
      };
      dispatch(saveFilterLoading());
      await axios.post(`${DOMAIN}/api/v1/data/recentlysold/`, body, config);
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
    minRooms,
    maxRooms,
    minBaths,
    maxBaths,
    minSqft,
    maxSqft,
    minLotSqft,
    maxLotSqft,
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
        min_beds: minRooms,
        max_beds: maxRooms,
        min_baths: minBaths,
        max_baths: maxBaths,
        min_sqft: minSqft,
        max_sqft: maxSqft,
        min_lot_sqft: minLotSqft,
        max_lot_sqft: maxLotSqft,
        for_zapier: forZapier,
      };
      dispatch(saveFilterLoading());
      await axios.post(`${DOMAIN}/api/v1/data/forsale/`, body, config);
      dispatch(saveFilter());
    } catch (error) {
      dispatch(
        saveFilterError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
      );
    }
  };

export const getCompanyDashboardDataAsync = (refreshed = false) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const { userInfo } = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access_token}`,
      },
    };
    dispatch(companyDashboardLoading());
    const { data } = await axios.get(`${DOMAIN}/api/v1/data/company_dashboard/`, config);    
    dispatch(companyDashboard(data));
  } catch (error) {
    dispatch(
      companyDashboardError(error.response && error.response.data.detail ? error.response.data.detail : error.message)
    );
    if (error.response.status === 403 && !refreshed) {
      dispatch(getRefreshToken(dispatch, getCompanyDashboardDataAsync(true)));
    } else {
      dispatch(logout());
    }
  }
}

