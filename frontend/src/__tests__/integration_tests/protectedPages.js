import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import ProtectedRoute from '../../components/ProtectedRoute';

// Mock react-redux hooks
import { useSelector as realUseSelector } from 'react-redux';

jest.mock('react-redux', () => ({
  ...jest.requireActual('react-redux'),
  useSelector: jest.fn(),
  useDispatch: jest.fn(),
}));

describe('ProtectedRoute', () => {
  let store;
  const initialState = {};
  const mockStore = configureStore();

  beforeEach(() => {
    jest.resetAllMocks(); // Reset all mocks before each test
  });

  it('redirects to /login when user is not authenticated', () => {
    const mockUnauthenticatedState = {
      auth: {
        userInfo: {
          userInfo: null,
          twoFA: false,
          loading: false,
          error: null,
        },
        registerInfo: {
          loading: false,
          error: null,
        },
        salesForce: {
          key: null,
          loading: false,
          error: null,
        },
      },
    };

    store = mockStore(mockUnauthenticatedState);

    realUseSelector.mockImplementation((selector) => selector(mockUnauthenticatedState));

    const { queryByText } = render(
      <Provider store={store}>
        <BrowserRouter>
          <ProtectedRoute>
            <div>Protected content</div>
          </ProtectedRoute>
        </BrowserRouter>
      </Provider>
    );

    // TODO: add actual test
  });
});
