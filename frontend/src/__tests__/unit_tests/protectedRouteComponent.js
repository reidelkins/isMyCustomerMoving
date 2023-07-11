import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import configureStore from 'redux-mock-store';
import ProtectedRoute from '../../components/ProtectedRoute';

const mockStore = configureStore([]);

describe("ProtectedRoute", () => {
  it("renders children for authenticated users", () => {
    const store = mockStore({
      auth: {
        userInfo: {
          userInfo: { otp_enabled: false },
          twoFA: true,
        },
      },
    });

    render(
      <Provider store={store}>
        <MemoryRouter>
          <ProtectedRoute path="/">
            <div>Protected Content</div>
          </ProtectedRoute>
        </MemoryRouter>
      </Provider>
    );

    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });

  it("redirects unauthenticated users", () => {
    const store = mockStore({
      auth: {
        userInfo: {
          userInfo: null,
          twoFA: false,
        },
      },
    });

    render(
      <Provider store={store}>
        <MemoryRouter>
          <ProtectedRoute path="/">
            <div>Protected Content</div>
          </ProtectedRoute>
        </MemoryRouter>
      </Provider>
    );

    // In real app, it would redirect to the login page.
    // In MemoryRouter without a route for "/login", it simply doesn't render the children.
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });
});
