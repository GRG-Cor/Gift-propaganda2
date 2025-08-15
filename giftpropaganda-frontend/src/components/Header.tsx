import React from 'react';
import styled from 'styled-components';
import { getAPIStatus } from '../api/news';
import SearchBar from './SearchBar';
import CategoryTabs from './CategoryTabs';
import { Category } from '../types';

const HeaderContainer = styled.header`
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--tg-theme-bg-color, #0f0f0f);
  border-bottom: 1px solid var(--tg-theme-hint-color, #333);
  padding: 10px 12px;
  backdrop-filter: blur(10px);
  
  @media (min-width: 768px) {
    padding: 12px 16px;
  }
`;

const HeaderTop = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--tg-theme-text-color, #ffffff);
  display: flex;
  align-items: center;
  gap: 8px;
  
  @media (min-width: 768px) {
    font-size: 20px;
  }
`;

const StatsBar = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--tg-theme-hint-color, #999);
  flex-wrap: wrap;
  
  @media (min-width: 768px) {
    gap: 16px;
    font-size: 14px;
  }
`;

const StatItem = styled.span<{ $color?: string }>`
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  color: ${props => props.$color || 'var(--tg-theme-hint-color, #999)'};
`;

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  categories: Category[];
}

const Header: React.FC<HeaderProps> = ({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  categories
}) => {
  return (
    <HeaderContainer>
      <HeaderTop>
        <Title>🎁 Gift Propaganda</Title>
      </HeaderTop>

      <StatsBar>
        <StatItem $color="#4ade80">СТАТЬИ +78</StatItem>
        <StatItem $color="#60a5fa">ПОСТЫ +20</StatItem>
        <StatItem $color="#a78bfa">НОВОСТИ +54</StatItem>
        <StatItem $color={getAPIStatus().apiHealth.local ? "#4ade80" : "#ef4444"}>
          {getAPIStatus().apiHealth.local ? "🟢 ЛОКАЛЬНЫЙ" : "🔴 ЛОКАЛЬНЫЙ"}
        </StatItem>
        <StatItem $color={getAPIStatus().apiHealth.prod ? "#4ade80" : "#ef4444"}>
          {getAPIStatus().apiHealth.prod ? "🟢 ПРОДАКШН" : "🔴 ПРОДАКШН"}
        </StatItem>
      </StatsBar>

      <SearchBar
        value={searchQuery}
        onChange={onSearchChange}
        placeholder="Поиск новостей..."
      />

      <CategoryTabs
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={onCategoryChange}
      />
    </HeaderContainer>
  );
};

export default Header; 