import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import userEvent from '@testing-library/user-event';
import configureStore from 'redux-mock-store';
import { prettyDOM } from '@testing-library/dom';
import ProtectedRoute from '../../components/ProtectedRoute';
import Home from '../../pages/dashboard/Home';

const mockStore = configureStore([]);

const renderWithRouter = (ui, { route = '/', store } = {}) => {
  window.history.pushState({}, 'Test page', route);

  return {
    user: userEvent.setup(),
    ...render(
      <Provider store={store}>
        <BrowserRouter>{ui}</BrowserRouter>
      </Provider>
    ),
  };
};

test('protected home route', () => {
  const mockReduceStore = mockStore({
    auth: {
      userInfo: {
        userInfo: null,
        twoFA: false,
      },
    },
  });
  renderWithRouter(
    <Provider store={mockReduceStore}>
      <ProtectedRoute>
        <Home />
      </ProtectedRoute>
    </Provider>,
    { route: '/dashboard', store: mockReduceStore }
  );

  // Try to access the protected route without being logged in
  expect(screen.getByText(/Log In Here/i)).toBeInTheDocument();
});
