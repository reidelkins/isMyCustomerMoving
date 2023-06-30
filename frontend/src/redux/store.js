import { configureStore, combineReducers } from '@reduxjs/toolkit';
import thunk from 'redux-thunk';
import authReducer from './actions/authActions';
import userReducer from './actions/usersActions';
import enterpriseReducer from './actions/enterpriseActions';

const reducer = combineReducers({
  auth: authReducer,
  user: userReducer,
  enterprise: enterpriseReducer,
});

const middleware = [thunk];

// const store = configureStore({reducer}, initialState, composeWithDevTools({ mageAge: 200 })(applyMiddleware(...middleware)));
const store = configureStore({ reducer, middleware, devTools: true });

export default store;
