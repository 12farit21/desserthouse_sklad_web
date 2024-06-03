import React, { useState, useEffect } from 'react';
import axios from 'axios';
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

  useEffect(() => {
    const intervalId = setInterval(() => {
      axios.post('/api/run_test_script')
        .then(response => {
          console.log(response.data);
        })
        .catch(error => {
          console.error("There was an error running the test script!", error);
        });
    }, 10000); // 10000ms = 10 seconds

    // Cleanup the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);


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
