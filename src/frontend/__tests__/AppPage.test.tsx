import React from 'react';
import { render, screen } from '@testing-library/react';
import AppPage from '@/app/app/page';

// Mock Recharts since it uses ResizeObserver which isn't fully supported in jsdom
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="mock-responsive-container" style={{ width: '100%', height: '100%' }}>
        {children}
      </div>
    ),
  };
});

describe('AppPage Layout and Component Integration', () => {
  it('renders the main operational dashboard successfully', () => {
    render(<AppPage />);
    
    // Check main header & branding
    expect(screen.getByText('Water analysis')).toBeInTheDocument();
    expect(screen.getByText('WaterForAll')).toBeInTheDocument();
  });

  it('renders the SampleInput component features', () => {
    render(<AppPage />);
    expect(screen.getByText('Test a water sample')).toBeInTheDocument();
    expect(screen.getByText('Live demo')).toBeInTheDocument();
    expect(screen.getByText('Safe Water')).toBeInTheDocument();
    expect(screen.getByText('Microbial Outbreak')).toBeInTheDocument();
    expect(screen.getByText('Chemical Spill')).toBeInTheDocument();
  });

  it('renders the DiagnosisPanel in its default state', () => {
    render(<AppPage />);
    expect(screen.getByText('Awaiting a sample')).toBeInTheDocument();
    expect(screen.getByText('Run a demo scenario or upload a sample to see the safety diagnosis.')).toBeInTheDocument();
  });

  it('renders the CommunityRisk component default state', () => {
    render(<AppPage />);
    expect(screen.getByText('Community risk')).toBeInTheDocument();
    expect(screen.getByText(/Select your area above/)).toBeInTheDocument();
  });
});
