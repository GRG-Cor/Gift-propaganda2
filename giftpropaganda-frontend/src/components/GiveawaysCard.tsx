import React from 'react';
import styled from 'styled-components';

const GiveawaysContainer = styled.div`
  width: 100%;
  margin-bottom: 16px;
`;

const GiveawaysButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px 24px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-align: left;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.08) 0%, transparent 50%);
    pointer-events: none;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
`;

const GiveawaysContent = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
`;

const GiveawaysIcon = styled.div`
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const GiveawaysText = styled.div`
  flex: 1;
`;

const GiveawaysTitle = styled.h3`
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const GiveawaysDescription = styled.p`
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.4;
`;

const ArrowIcon = styled.div`
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
  opacity: 0.9;
`;

interface GiveawaysCardProps {
  onClick?: () => void;
}

const GiveawaysCard: React.FC<GiveawaysCardProps> = ({ onClick }) => {
  return (
    <GiveawaysContainer>
      <GiveawaysButton onClick={onClick}>
        <GiveawaysContent>
          <GiveawaysIcon>
            🎁
          </GiveawaysIcon>
          <GiveawaysText>
            <GiveawaysTitle>
              Giveaways
              🎁
            </GiveawaysTitle>
            <GiveawaysDescription>
              Join giveaways and win collectible gifts
            </GiveawaysDescription>
          </GiveawaysText>
        </GiveawaysContent>
        <ArrowIcon>
          ›
        </ArrowIcon>
      </GiveawaysButton>
    </GiveawaysContainer>
  );
};

export default GiveawaysCard; 