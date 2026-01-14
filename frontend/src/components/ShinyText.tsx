'use client';

import { ReactNode } from 'react';
import './ShinyText.css';

interface ShinyTextProps {
  children: ReactNode;
  className?: string;
  shimmerWidth?: number;
  speed?: number;
}

export default function ShinyText({ 
  children, 
  className = '',
  shimmerWidth = 100,
  speed = 3
}: ShinyTextProps) {
  return (
    <span 
      className={`shiny-text ${className}`}
      style={{
        '--shimmer-width': `${shimmerWidth}px`,
        '--animation-speed': `${speed}s`
      } as React.CSSProperties}
    >
      {children}
    </span>
  );
}
