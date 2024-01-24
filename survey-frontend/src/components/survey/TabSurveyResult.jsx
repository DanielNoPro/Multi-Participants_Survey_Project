import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import { Chart } from "react-google-charts";
import { fetchGetSurveyStatistics } from '@/redux/slices/surveySlice';
import { Button, Select, Table } from 'antd';

const columns = [
    {
        title: 'Option',
        dataIndex: 'value',
        key: 'value',
    },
    {
        title: 'Count',
        dataIndex: 'count',
        key: 'count',
    }
];

const TabSurveyResult = ({ slug }) => {
    const dispatch = useDispatch()
    const { statistics, loadingSurvey } = useSelector((state) => state.survey)
    const [type, setType] = useState("Bar")

    console.log(statistics);

    useEffect(() => {
        dispatch(fetchGetSurveyStatistics(slug))
    }, []);

    const handleChange = (value) => {
        setType(value);
    };

    const SetStatOptions = (title) => {
        let options = {}
        switch (type) {
            case "Bar":
                return options = {
                    chart: {
                        title: title,
                    },
                };
            case "PieChart":
                return options = {
                    title: title,
                };
            default:
                break;
        }
    }

    const SetStatData = (statistics) => {
        const newArray = statistics.map(({ value, count }) => ([value, count]));
        const statArr = [
            ['value', 'frequency'],
            ...newArray
        ]
        return statArr;
    }

    return (
        <>
            <Select
                defaultValue="Bar"
                style={{
                    width: 120,
                    marginBottom: 20
                }}
                onChange={handleChange}
                options={[
                    {
                        value: 'Bar',
                        label: 'Bar Chart',
                    },
                    {
                        value: 'PieChart',
                        label: 'Pie Chart',
                    },
                    {
                        value: 'table',
                        label: 'Table'
                    }
                ]}
            />
            <div>
                {type == 'table' ? (
                    <div>
                        {statistics?.map((item, index) => (
                            <div style={{marginBottom: '30px'}}>
                                <b>{item.question}</b>
                                <Table dataSource={item.statistics} columns={columns} pagination={false}/>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div>
                        {statistics?.map((item, index) => (
                            <Chart
                                key={index}
                                chartType={type}
                                data={SetStatData(item.statistics)}
                                options={SetStatOptions(item.question)}
                                width={"100%"}
                                height={"400px"}
                            />
                        ))}
                    </div>
                )}
            </div>
        </>
    );
};

export default TabSurveyResult;