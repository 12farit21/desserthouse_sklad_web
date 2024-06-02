import React, { useState, useMemo, useEffect } from 'react';
import './DealList.css';
import { API_URL } from '../../config';

const fields = [
  { id: 'id_deal', label: 'ID Сделки' },
  { id: 'deal_name', label: 'Название' },
  { id: 'stage_name', label: 'Этап' },
  { id: 'client', label: 'Клиент' },
  { id: 'opportunity', label: 'Возможность' },
  { id: 'currency_id', label: 'Валюта' },
  { id: 'payment_method', label: 'Метод оплаты' },
  { id: 'full_name', label: 'Ответственный' },
  { id: 'date_create', label: 'Дата создания' },
  { id: 'date_delivery', label: 'Дата доставки' },
  { id: 'date_payment', label: 'Дата оплаты' },
  { id: 'city', label: 'Город' },
  { id: 'voronka_name', label: 'Воронка' },
];

const productFields = [
  { id: 'id', label: 'ID' },
  { id: 'id_deal', label: 'ID сделки' },
  { id: 'product_id', label: 'ID продукта' },
  { id: 'product_name', label: 'Название продукта' },
  { id: 'price', label: 'Цена' },
  { id: 'quantity', label: 'Кол-во' },
  { id: 'measure', label: 'Ед. измерения' },
  { id: 'store_id', label: 'Склад' },
];

function DealList() {
  const [dateType, setDateType] = useState({});
  const [inputData, setInputData] = useState({});
  const [responseData, setResponseData] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });
  const [selectedDeal, setSelectedDeal] = useState(null);
  const [dealProducts, setDealProducts] = useState([]);

  const sortedItems = useMemo(() => {
    let sortableItems = [...responseData];
    if (sortConfig.key !== null) {
      sortableItems.sort((a, b) => {
        if (a[sortConfig.key] < b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (a[sortConfig.key] > b[sortConfig.key]) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return sortableItems;
  }, [responseData, sortConfig]);

  const requestSort = key => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const getSortDirectionArrow = (key) => {
    if (sortConfig.key === key) {
      return sortConfig.direction === 'ascending' ? <span className="sort-arrow asc"></span> : <span className="sort-arrow desc"></span>;
    }
    return null;
  };

  const handleCheckboxChange = (id, checked) => {
    if (checked) {
      setInputData({ ...inputData, [id]: '' });
    } else {
      const newData = { ...inputData };
      delete newData[id];
      setInputData(newData);
    }
  };

  const handleInputChange = (id, value) => {
    setInputData({ ...inputData, [id]: value });
  };

  const handleDateTypeChange = (type, field, checked) => {
    const newDateType = { ...dateType };
    if (checked) {
      newDateType[field] = type;
      if (type === 'exact') {
        setInputData({ ...inputData, [`${field}Exact`]: '' });
      } else if (type === 'range') {
        setInputData({ ...inputData, [`${field}Start`]: '', [`${field}End`]: '' });
      }
    } else {
      delete newDateType[field];
      const newData = { ...inputData };
      if (type === 'exact') {
        delete newData[`${field}Exact`];
      } else if (type === 'range') {
        delete newData[`${field}Start`];
        delete newData[`${field}End`];
      }
      setInputData(newData);
    }
    setDateType(newDateType);
  };

  const handleSubmit = async () => {
    const response = await fetch(`${API_URL}/api/deals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputData)
    });
    const data = await response.json();
    setResponseData(data);
  };

  const handleRowClick = (deal) => {
    setSelectedDeal(deal);
    setDealProducts([]);
  };

  const handleClosePopup = () => {
    setSelectedDeal(null);
    setDealProducts([]);
  };

  const handleViewProducts = async () => {
    if (selectedDeal) {
      const response = await fetch(`${API_URL}/api/deal_products/${selectedDeal.id_deal}`);
      const data = await response.json();
      setDealProducts(data);
    }
  };

  return (
    <div>
      <div className="container">
        {fields.map(field => (
          <div key={field.id} className="field">
            <label>
              <input
                type="checkbox"
                checked={inputData.hasOwnProperty(field.id)}
                onChange={e => handleCheckboxChange(field.id, e.target.checked)}
              />
              {field.label}
            </label>
            {['date_create', 'date_delivery', 'date_payment'].includes(field.id) && inputData.hasOwnProperty(field.id) && (
              <>
                <label>
                  <input
                    type="checkbox"
                    checked={dateType[field.id] === 'exact'}
                    onChange={(e) => handleDateTypeChange('exact', field.id, e.target.checked)}
                  />
                  Точная дата
                </label>
                {dateType[field.id] === 'exact' && (
                  <input
                    type="date"
                    value={inputData[`${field.id}Exact`]}
                    onChange={(e) => handleInputChange(`${field.id}Exact`, e.target.value)}
                  />
                )}

                <label>
                  <input
                    type="checkbox"
                    checked={dateType[field.id] === 'range'}
                    onChange={(e) => handleDateTypeChange('range', field.id, e.target.checked)}
                  />
                  Диапазон дат
                </label>
                {dateType[field.id] === 'range' && (
                  <>
                    <input
                      type="date"
                      value={inputData[`${field.id}Start`]}
                      onChange={(e) => handleInputChange(`${field.id}Start`, e.target.value)}
                      placeholder="Start Date"
                    />
                    <input
                      type="date"
                      value={inputData[`${field.id}End`]}
                      onChange={(e) => handleInputChange(`${field.id}End`, e.target.value)}
                      placeholder="End Date"
                    />
                  </>
                )}
              </>
            )}
            {!['date_create', 'date_delivery', 'date_payment'].includes(field.id) && inputData.hasOwnProperty(field.id) && (
              <input
                type="text"
                value={inputData[field.id]}
                onChange={e => handleInputChange(field.id, e.target.value)}
                placeholder={`Введи ${field.label.toLowerCase()}`}
              />
            )}
          </div>
        ))}
        <button id='searchButton' onClick={handleSubmit}>Search</button>
      </div>

      {responseData && responseData.length > 0 && (
        <div>
          <p>Количество записей: {sortedItems.length}</p>
          <table className="table">
            <thead>
              <tr>
                {fields.map(field => (
                  <th key={field.id} onClick={() => requestSort(field.id)}>
                    {field.label} {getSortDirectionArrow(field.id)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedItems.map((item, index) => (
                <tr key={index} onClick={() => handleRowClick(item)}>
                  {fields.map(field => (
                    <td key={field.id}>{item[field.id]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

        </div>
      )}

      {selectedDeal && (
        <div className="popup">
          <div className="popup-content">
            <h3>{selectedDeal.deal_name}</h3>
            <div className="button-container">
              <button onClick={handleViewProducts}>Товары</button>
              <button onClick={handleClosePopup}>Закрыть</button>
            </div>
            {dealProducts.length > 0 && (
              <div>
                <h4>Товары:</h4>
                <table className="table">
                  <thead>
                    <tr>
                      {productFields.map(field => (
                        <th key={field.id}>{field.label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {dealProducts.map((product, index) => (
                      <tr key={index}>
                        {productFields.map(field => (
                          <td key={field.id}>{product[field.id]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default DealList;
