import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { SettingsPage } from '../pages/SettingsPage';
import { api } from '../services/api';

vi.mock('../services/api', () => ({
  api: {
    getHealth: vi.fn(),
  },
}));

describe('SettingsPage Component', () => {
  it('renders system documentation, formulas, and operational limits', async () => {
    (api.getHealth as any).mockResolvedValue({
      status: 'healthy',
      version: '1.0.0',
      database: 'SQLite',
    });

    render(<SettingsPage />);

    expect(screen.getByText(/System Settings & Documentation/i)).toBeInTheDocument();
    expect(screen.getByText(/Deterministic Fix Prioritization Formula/i)).toBeInTheDocument();
    expect(screen.getByText(/SEO Health Score Calculation/i)).toBeInTheDocument();
    expect(screen.getByText(/Server-Side Request Forgery \(SSRF\) Firewall/i)).toBeInTheDocument();
    expect(screen.getByText(/50 Pages/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/System Operational/i)).toBeInTheDocument();
    });
  });
});
