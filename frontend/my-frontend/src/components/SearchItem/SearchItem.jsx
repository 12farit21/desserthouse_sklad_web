import React, { useState, useMemo, useEffect } from 'react';
import './SearchItem.css';
import { API_URL } from '../../config';

const fields = [
  { id: 'id', label: 'id' },
  { id: 'iblockId', label: 'Идентификатор раздела' },
  { id: 'quantity', label: 'Кол-во' },
  { id: 'quantity_proizvodstvo_1', label: 'Кол-во в Производство' },
  { id: 'quantity_astana_2', label: 'Кол-во в Астана' },
  { id: 'quantity_almaty_4', label: 'Кол-во в Алматы' },
  { id: 'quantity_shymkent_6', label: 'Кол-во в Шымкенте' },
  { id: 'quantity_karaganda_8', label: 'Кол-во в Караганде' },
  { id: 'timestampX', label: 'Дата изменения' }
];

const dealFields = [
  { id: 'id_deal', label: 'ID Сделки' },
  { id: 'deal_name', label: 'Название сделки' },
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

function SearchForm() {
  const [dateType, setDateType] = useState(null);  // To track "Точная дата" or "Диапазон дат"
  const [inputData, setInputData] = useState({});
  const [responseData, setResponseData] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });
  const [sections, setSections] = useState([]);
  const [fetchError, setFetchError] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [dealData, setDealData] = useState([]);

  useEffect(() => {
    const fetchSections = async () => {
      try {
        const response = await fetch(`${API_URL}/api/get_razdel_list`);
        const data = await response.json();
        setSections(data);
      } catch (error) {
        setFetchError('Failed to fetch section data');
        console.error('Fetch error:', error);
      }
    };

    if (inputData.hasOwnProperty('iblockId')) {
      fetchSections();
    }
  }, [inputData.iblockId]);

  const handleSectionCheckboxChange = (id, checked) => {
    const newIblockSectionIds = { ...inputData.iblockSectionId } || {};
    if (checked) {
      newIblockSectionIds[id] = true;
    } else {
      delete newIblockSectionIds[id];
    }
    setInputData({ ...inputData, iblockSectionId: newIblockSectionIds });
  };

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

  const handleSubmit = async () => {
    const response = await fetch(`${API_URL}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputData)
    });
    const data = await response.json();
    setResponseData(data);
  };

  const handleDateTypeChange = (type, checked) => {
    if (checked) {
      setDateType(type);
      if (type === 'exact') {
        setInputData({ ...inputData, 'exactDate': '' });
      } else if (type === 'range') {
        setInputData({ ...inputData, 'startDate': '', 'endDate': '' });
      }
    } else {
      setDateType(null);
      const newData = { ...inputData };
      if (type === 'exact') {
        delete newData['exactDate'];
      } else if (type === 'range') {
        delete newData['startDate'];
        delete newData['endDate'];
      }
      setInputData(newData);
    }
  };

  const handleRowClick = (item) => {
    setSelectedItem(item);
    setDealData([]); // Clear previous deal data
  };

  const handleClosePopup = () => {
    setSelectedItem(null);
    setDealData([]);
  };

  const handleDealClick = async () => {
    if (selectedItem) {
      const response = await fetch(`${API_URL}/api/deal_by_product/${selectedItem.id}`);
      const data = await response.json();
      setDealData(data);
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
            {field.id === 'iblockId' && inputData.hasOwnProperty('iblockId') && sections.map(section => (
              <label key={section.id}>
                <input
                  type="checkbox"
                  checked={inputData.iblockSectionId && inputData.iblockSectionId[section.id]}
                  onChange={e => handleSectionCheckboxChange(section.id, e.target.checked)}
                />
                {section.name}
              </label>
            ))}
            {field.id !== 'iblockId' && inputData.hasOwnProperty(field.id) && (
              <input
                type="text"
                value={inputData[field.id]}
                onChange={e => handleInputChange(field.id, e.target.value)}
                placeholder={`Введи ${field.label.toLowerCase()}`}
              />
            )}

            {field.id === 'timestampX' && inputData.hasOwnProperty('timestampX') && (
              <>
                <label>
                  <input
                    type="checkbox"
                    checked={dateType === 'exact'}
                    onChange={(e) => handleDateTypeChange('exact', e.target.checked)}
                  />
                  Точная дата
                </label>
                {dateType === 'exact' && (
                  <input
                    type="date"
                    value={inputData['exactDate']}
                    onChange={(e) => handleInputChange('exactDate', e.target.value)}
                  />
                )}

                <label>
                  <input
                    type="checkbox"
                    checked={dateType === 'range'}
                    onChange={(e) => handleDateTypeChange('range', e.target.checked)}
                  />
                  Диапазон дат
                </label>
                {dateType === 'range' && (
                  <>
                    <input
                      type="date"
                      value={inputData['startDate']}
                      onChange={(e) => handleInputChange('startDate', e.target.value)}
                      placeholder="Start Date"
                    />
                    <input
                      type="date"
                      value={inputData['endDate']}
                      onChange={(e) => handleInputChange('endDate', e.target.value)}
                      placeholder="End Date"
                    />
                  </>
                )}
              </>
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
                <th onClick={() => requestSort('id')}>ID {getSortDirectionArrow('id')}</th>
                <th onClick={() => requestSort('iblockSectionId')}>Идентификатор раздела {getSortDirectionArrow('iblockSectionId')}</th>
                <th onClick={() => requestSort('name')}>Название продукта {getSortDirectionArrow('name')}</th>
                <th onClick={() => requestSort('quantity')}>Кол-во {getSortDirectionArrow('quantity')}</th>
                <th onClick={() => requestSort('quantity_proizvodstvo_1')}>Производство {getSortDirectionArrow('quantity_proizvodство_1')}</th>
                <th onClick={() => requestSort('quantity_astana_2')}>Астана {getSortDirectionArrow('quantity_astana_2')}</th>
                <th onClick={() => requestSort('quantity_almaty_4')}>Алматы {getSortDirectionArrow('quantity_almaty_4')}</th>
                <th onClick={() => requestSort('quantity_shymkent_6')}>Шымкент {getSortDirectionArrow('quantity_shymkent_6')}</th>
                <th onClick={() => requestSort('quantity_karaganda_8')}>Караганда {getSortDirectionArrow('quantity_karaganda_8')}</th>
                <th onClick={() => requestSort('timestampX')}>Время изменения {getSortDirectionArrow('timestampX')}</th>
              </tr>
            </thead>
            <tbody>
              {sortedItems.map((item, index) => (
                <tr key={index} onClick={() => handleRowClick(item)}>
                  <td>{item.id}</td>
                  <td>{item.iblockSectionId}</td>
                  <td>{item.name}</td>
                  <td>{item.quantity}</td>
                  <td>{item.quantity_proizvodstvo_1}</td>
                  <td>{item.quantity_astana_2}</td>
                  <td>{item.quantity_almaty_4}</td>
                  <td>{item.quantity_shymkent_6}</td>
                  <td>{item.quantity_karaganda_8}</td>
                  <td>{item.timestampX}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedItem && (
        <div className="popup">
          <div className="popup-content">
            <h3>{selectedItem.name}</h3>
            <div className="button-container">
              <button onClick={handleDealClick}>Сделка</button>
              <button onClick={handleClosePopup}>Закрыть</button>
            </div>
            {dealData.length > 0 && (
              <div className="table-container">
                <h4>Данные сделки:</h4>
                <table className="table">
                  <thead>
                    <tr>
                      {dealFields.map(field => (
                        <th key={field.id}>{field.label}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {dealData.map((deal, index) => (
                      <tr key={index}>
                        {dealFields.map(field => (
                          <td key={field.id}>{deal[field.id]}</td>
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

export default SearchForm;
