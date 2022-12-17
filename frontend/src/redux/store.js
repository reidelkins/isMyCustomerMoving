import { applyMiddleware } from 'redux';
import { configureStore, combineReducers } from '@reduxjs/toolkit';
import thunk from 'redux-thunk';
import { composeWithDevTools } from 'redux-devtools-extension';
import { loginReducer, registerReducer, resetRequestReducer } from './reducers/authReducers';
import { usersReducer, companyReducer } from './reducers/usersReducers';

const reducer = combineReducers({
  userLogin: loginReducer,
  userRgister: registerReducer,
  userResetRequest: resetRequestReducer,
  listUser: usersReducer,
  company: companyReducer,
});

const userInfoFromStorage = localStorage.getItem('userInfo') ? JSON.parse(localStorage.getItem('userInfo')) : null;

const initialState = {
  userLogin: { userInfo: userInfoFromStorage },
};
const middleware = [thunk];

const store = configureStore({reducer}, initialState, composeWithDevTools({ mageAge: 200 })(applyMiddleware(...middleware)));

export default store;
