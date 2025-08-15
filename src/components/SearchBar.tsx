import React from 'react';
import styled from 'styled-components';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

const SearchContainer = styled.div`
  position: relative;
  margin-bottom: 12px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 10px 16px 10px 40px;
  border: 1px solid var(--tg-theme-hint-color, #333);
  border-radius: 8px;
  background: var(--tg-theme-secondary-bg-color, #1a1a1a);
  color: var(--tg-theme-text-color, #ffffff);
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s ease;
  box-sizing: border-box;

  &::placeholder {
    color: var(--tg-theme-hint-color, #999);
  }

  &:focus {
    outline: none;
    border-color: var(--tg-theme-button-color, #0088cc);
    box-shadow: 0 0 0 3px rgba(0, 136, 204, 0.1);
  }

  &:hover {
    border-color: var(--tg-theme-button-color, #0088cc);
  }
`;

const SearchIcon = styled.div`
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--tg-theme-hint-color, #999);
  font-size: 16px;
  pointer-events: none;
`;

const ClearButton = styled.button<{ $visible: boolean }>`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--tg-theme-hint-color, #999);
  cursor: pointer;
  font-size: 16px;
  opacity: ${props => props.$visible ? 1 : 0};
  transition: all 0.2s ease;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: var(--tg-theme-text-color, #ffffff);
  }
`;

const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  placeholder = "Поиск..."
}) => {
  const handleClear = () => {
    onChange('');
  };

  return (
    <SearchContainer>
      <SearchIcon>🔍</SearchIcon>
      <SearchInput
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
      <ClearButton
        $visible={value.length > 0}
        onClick={handleClear}
        type="button"
      >
        ✕
      </ClearButton>
    </SearchContainer>
  );
};

export default SearchBar;
