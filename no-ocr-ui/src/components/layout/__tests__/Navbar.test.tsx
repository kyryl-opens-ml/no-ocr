import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Navbar from '../Navbar';
import { useAuthStore } from '../../../stores/authStore';

describe('Navbar', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isLoading: false });
  });

  it('renders main navigation links', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );
    expect(screen.getByText('NoOCR')).toBeInTheDocument();
    expect(screen.getByText('AI Search')).toBeInTheDocument();
    expect(screen.getByText('Create Case')).toBeInTheDocument();
  });
});
