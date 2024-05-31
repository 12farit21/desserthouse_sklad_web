import React, { useState } from 'react';
import AllRows from '../../components/allRows/allRows'; 
import SearchItem from '../../components/SearchItem/SearchItem';
import DealList from '../../components/DealList/DealList';
import './home.css'
const Home = () => {
  const [showAllRows, setShowAllRows] = useState(false);  
  const [showSearchItem, setShowSearchItem] = useState(false); 
  const [showDealList, setShowDealList] = useState(false); 

  const handleShowAllRows = () => {
    setShowAllRows(true);       
    setShowSearchItem(false);   
    setShowDealList(false);
  };

  const handleShowSearchItem = () => {
    setShowSearchItem(true);   
    setShowAllRows(false);     
    setShowDealList(false);
  };

  const handleShowDealList = () => {
    setShowDealList(true);
    setShowAllRows(false);
    setShowSearchItem(false);
  };

  return (
    <div>
      <h1 id = 'zagolovok-home'>Dessert House</h1>
      <button onClick={handleShowAllRows}>Показать все товары</button>  
      <button onClick={handleShowSearchItem}>Поиск товара</button>
      <button onClick={handleShowDealList}>Сделки</button>  
      {showAllRows && <AllRows />}  
      {showSearchItem && <SearchItem />}  
      {showDealList && <DealList />}  
    </div>
  );
};

export default Home;
