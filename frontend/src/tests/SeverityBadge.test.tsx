import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { SeverityBadge } from '../components/SeverityBadge';

describe('SeverityBadge Component', () => {
  it('renders critical severity with correct text and style', () => {
    render(<SeverityBadge severity="critical" />);
    const badge = screen.getByText(/critical/i);
    expect(badge).toBeInTheDocument();
  });

  it('renders high severity correctly', () => {
    render(<SeverityBadge severity="high" />);
    expect(screen.getByText(/high/i)).toBeInTheDocument();
  });

  it('renders medium severity correctly', () => {
    render(<SeverityBadge severity="medium" />);
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
  });
});
