import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ScoreBadge } from '../components/ScoreBadge';

describe('ScoreBadge Component', () => {
  it('renders high score with Excellent grade', () => {
    render(<ScoreBadge score={88.5} />);
    expect(screen.getByText('88.5')).toBeInTheDocument();
    expect(screen.getByText(/excellent/i)).toBeInTheDocument();
  });

  it('renders moderate score with Fair grade', () => {
    render(<ScoreBadge score={68.0} />);
    expect(screen.getByText('68.0')).toBeInTheDocument();
    expect(screen.getByText(/fair/i)).toBeInTheDocument();
  });

  it('renders low score with Poor grade', () => {
    render(<ScoreBadge score={45.0} />);
    expect(screen.getByText('45.0')).toBeInTheDocument();
    expect(screen.getByText(/poor/i)).toBeInTheDocument();
  });
});
