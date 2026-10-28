import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import { LandingPage } from '../pages/LandingPage';

describe('LandingPage Component', () => {
  it('renders hero title and input field', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/Find SEO Issues/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/https:\/\/example.com/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start audit/i })).toBeInTheDocument();
  });
});
