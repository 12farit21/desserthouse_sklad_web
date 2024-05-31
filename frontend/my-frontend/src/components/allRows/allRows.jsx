import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './allRows.css';

const AllRows = () => {
    const [data, setData] = useState([]);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });

    const fetchData = async () => {
        try {
            const response = await axios.get('http://localhost:5000/api/data');
            setData(response.data);
        } catch (error) {
            console.error('There was an error fetching data:', error);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const sortedItems = React.useMemo(() => {
        let sortableItems = [...data];
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
    }, [data, sortConfig]);

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

    return (
        <div>
            <p>Количество записей: {sortedItems.length}</p>
            <table className="table">
                <thead>
                    <tr>
                        <th onClick={() => requestSort('id')}>ID {getSortDirectionArrow('id')}</th>
                        <th onClick={() => requestSort('iblockSectionId')}>Идентификатор раздела {getSortDirectionArrow('iblockSectionId')}</th>
                        <th onClick={() => requestSort('name')}>Название продукта {getSortDirectionArrow('name')}</th>
                        <th onClick={() => requestSort('quantity')}>Кол-во {getSortDirectionArrow('quantity')}</th>
                        <th onClick={() => requestSort('quantity_proizvodstvo_1')}>Производство {getSortDirectionArrow('quantity_proizvodstvo_1')}</th>
                        <th onClick={() => requestSort('quantity_astana_2')}>Астана {getSortDirectionArrow('quantity_astana_2')}</th>
                        <th onClick={() => requestSort('quantity_almaty_4')}>Алматы {getSortDirectionArrow('quantity_almaty_4')}</th>
                        <th onClick={() => requestSort('quantity_shymkent_6')}>Шымкент {getSortDirectionArrow('quantity_shymkent_6')}</th>
                        <th onClick={() => requestSort('quantity_karaganda_8')}>Караганда {getSortDirectionArrow('quantity_karaganda_8')}</th>
                        <th onClick={() => requestSort('timestampX')}>Время изменения {getSortDirectionArrow('timestampX')}</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedItems.map((item, index) => (
                        <tr key={index}>
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
    );
};

export default AllRows;
