import React from 'react';
import './FormGroup.css';

interface FormGroupProps {
  label: string;
  children: React.ReactNode;
  className?: string;
}

export const FormGroup: React.FC<FormGroupProps> = ({
  label,
  children,
  className = ''
}) => {
  return (
    <div className={`form-group ${className}`}>
      <label>{label}</label>
      {children}
    </div>
  );
};
