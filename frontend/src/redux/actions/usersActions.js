import axios from 'axios';
import { createSlice } from '@reduxjs/toolkit';
import { DOMAIN } from '../constants';
import { logout } from './authActions';


export const userSlice = createSlice({
  name: "user",
  initialState: {
    clientsInfo: {
      loading: false,
      error: null,
      CLIENTLIST: [],
    },
    usersInfo: {
      loading: false,
      error: null,
      USERLIST: [],
    },
    progress: {
      complete: true,
      error: null,
      value: 0,
      deleted: 0,
      loading: false,
    }
  },
  reducers: {
    // -----------------  CLIENTS  -----------------
    clients: (state, action) => {
      state.clientsInfo.CLIENTLIST = action.payload;
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
    },
    moreClients: (state, action) => {
      state.clientsInfo.CLIENTLIST = [...state.clientsInfo.CLIENTLIST, ...action.payload];
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
    },
    clientsError: (state, action) => {
      state.clientsInfo.error = action.payload;
      state.clientsInfo.loading = false;
      state.clientsInfo.CLIENTLIST = [];
    },
    clientsLoading: (state) => {
      state.clientsInfo.loading = true;
      state.clientsInfo.CLIENTLIST = [];
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

    // TODO
    sendNewUserEmail: (state) => {
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
    },
    updateNote: (state) => {
      state.clientsInfo.loading = false;
      state.clientsInfo.error = null;
    },

    // -----------------  PROGRESS  -----------------
    progress: (state, action) => {
      state.progress.value = action.payload.progress;
      state.progress.complete = false;
      state.clientsInfo.CLIENTLIST = action.payload.clients;
      state.progress.deleted = action.payload.deleted;

    },

    progressDone: (state) => {
      state.progress.complete = true;
      state.progress.value = 0;
      state.progress.loading = false;
    },

    progressError: (state, action) => {
      state.progress.error = action.payload.progress;
      state.progress.complete = true;
      state.progress.value = 0;
    },

    progressLoading: (state) => {
      state.progress.loading = true;
    }

  },
});

export const { clients, moreClients, clientsLoading, clientsError, users, usersLoading, usersError, progress, progressDone, progressError, progressLoading } = userSlice.actions;
export const selectClients = (state) => state.user.clientsInfo;
export const selectUsers = (state) => state.user.usersInfo;
export const selectProgress = (state) => state.user.progress;
export default userSlice.reducer;

export const usersAsync = () => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    dispatch(usersLoading());
    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/users/${userInfo.company.id}`, config);
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    dispatch(logout());
  }
};

export const deleteUserAsync = (ids) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;
    const {id: company} = userInfo.company;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    dispatch(usersLoading());
    const { data } = await axios.delete(`${DOMAIN}/api/v1/accounts/manageuser/${company}/`, { data: ids}, config);
    dispatch(users(data));
  } catch (error) {
    dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const clientsAsync = () => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    dispatch(clientsLoading());
    // print how long it takes to get data
    console.time('clients');
    const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/clients/${userInfo.company.id}?page=1&per_page=1000`, config);
    dispatch(clients(data.results));
    const loops = Math.ceil(data.count / 1000);
    let i = 2;
    /* eslint-disable no-plusplus */
    for (i; i <= loops; i++) {
      const { data: newData } = await axios.get(`${DOMAIN}/api/v1/accounts/clients/${userInfo.company.id}?page=${i}&per_page=1000`, config);
      dispatch(moreClients(newData.results));
    }
  } catch (error) {
    localStorage.removeItem('userInfo');
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
    dispatch(logout());
  }
};

export const deleteClientAsync = (ids) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    dispatch(clientsLoading());
    const chunkSize = 1000;
    let i = 0;
    for (i; i < ids.length; i += chunkSize) {
      const chunk = ids.slice(i, i + chunkSize);
      await axios.delete(`${DOMAIN}/api/v1/accounts/updateclient/`, { data: {'clients': chunk}}, config);
    }
    const chunk = ids.slice(i, i + chunkSize);
    await axios.delete(`${DOMAIN}/api/v1/accounts/updateclient/`, { data: {'clients': chunk}}, config);
    dispatch(clientsAsync());
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const updateClientAsync = (id, contacted, note) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    dispatch(clientsLoading());
    await axios.put(`${DOMAIN}/api/v1/accounts/updateclient/`, { 'clients': id, contacted, note }, config);
    dispatch(clientsAsync());
  } catch (error) {
    dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const serviceTitanSync = () => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;
    const {id: company} = userInfo.company;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    // dispatch(usersLoading());
    const {data} = await axios.get(`${DOMAIN}/api/v1/accounts/servicetitan/${company}/`, config);
    dispatch(clients(data.clients));
    dispatch(getUpdates(data.updateId));
  } catch (error) {
    throw new Error(error);
    // dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const createCompany = (company, email) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };

    await axios.post(
      `${DOMAIN}/api/v1/accounts/createCompany/`,
      { 'name': company, email},
      config
    );

  } catch (error) {
    throw new Error(error);
  }
};

export const manageUser = (email) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };

     dispatch(usersLoading());
    const {data} = await axios.post(
      `${DOMAIN}/api/v1/accounts/manageuser/${userInfo.company.id}/`,
      { email },
      config
    );
    dispatch(users(data));

    } catch (error) {
      dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const makeAdminAsync = (userId) => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };

    dispatch(usersLoading());
    const {data} = await axios.post(
      `${DOMAIN}/api/v1/accounts/manageuser/${userId}/`,
      config
    );
    dispatch(users(data));

    } catch (error) {
      dispatch(usersError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const getUpdates = (updateId) => async (dispatch, getState) => {
  try {
    dispatch(progressLoading());
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;

    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    setTimeout(async () => {
      const { data } = await axios.get(`${DOMAIN}/api/v1/accounts/updates/${updateId}/`, config)
      dispatch(progress(data))

      if (data.complete !== true) {
        dispatch(getUpdates(updateId));
      } else {
        dispatch(progressDone());
        dispatch(clientsAsync());
      }
    }, 1000);
    
  } catch (error) {
    dispatch(progressError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
  }
};

export const uploadClientsAsync = (customers) => async (dispatch, getState) => {
   try {
     const reduxStore = getState();
     const {userInfo} = reduxStore.auth.userInfo;
     const {id: company} = userInfo.company;

     const config = {
       headers: {
         'Content-type': 'application/json',
         Authorization: `Bearer ${userInfo.access}`,
       },
     };
    //  dispatch(clientsLoading());
    const { data } = await axios.post(`${DOMAIN}/api/v1/accounts/upload/${company}/`, customers, config);
    dispatch(getUpdates(data.updateId));
   } catch (error) {
     dispatch(clientsError(error.response && error.response.data.detail ? error.response.data.detail : error.message));
   }
 };

export const update = () => async (dispatch, getState) => {
  try {
    const reduxStore = getState();
    const {userInfo} = reduxStore.auth.userInfo;
    const config = {
      headers: {
        'Content-type': 'application/json',
        Authorization: `Bearer ${userInfo.access}`,
      },
    };
    await axios.get(`${DOMAIN}/api/v1/accounts/update/${userInfo.company.id}`, config);
  } catch (error) {
    throw new Error(error);
  }
};