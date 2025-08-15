import React from 'react';
import styled from 'styled-components';
import { Category } from '../types';

const CategoryTabsContainer = styled.div`
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 8px 0 4px 0;
  margin-bottom: 8px;
  
  &::-webkit-scrollbar {
    height: 3px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--tg-theme-hint-color, #333);
    border-radius: 2px;
  }
`;

const CategoryTab = styled.button<{ $active: boolean }>`
  padding: 6px 12px;
  border: none;
  border-radius: 16px;
  background: ${props => props.$active 
    ? 'var(--tg-theme-button-color, #0088cc)' 
    : 'var(--tg-theme-secondary-bg-color, #1a1a1a)'};
  color: ${props => props.$active 
    ? 'var(--tg-theme-button-text-color, #ffffff)' 
    : 'var(--tg-theme-text-color, #ffffff)'};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: fit-content;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 136, 204, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
`;

interface CategoryTabsProps {
  categories: Category[];
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
}

const CategoryTabs: React.FC<CategoryTabsProps> = ({
  categories,
  selectedCategory,
  onCategoryChange
}) => {
  return (
    <CategoryTabsContainer>
      {categories.map(category => (
        <CategoryTab
          key={category.id}
          $active={selectedCategory === category.id}
          onClick={() => onCategoryChange(category.id)}
        >
          {category.icon && <span>{category.icon}</span>}
          <span>{category.name}</span>
        </CategoryTab>
      ))}
    </CategoryTabsContainer>
  );
};

export default CategoryTabs; 