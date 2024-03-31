import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import { Chart } from "react-google-charts";
import { fetchGetSurveyStatistics } from '@/redux/slices/surveySlice';
import { Button, Pagination, Select, Table } from 'antd';

const columns = [
    {
        title: 'Answer content',
        dataIndex: 'value',
        key: 'value',
    },
    {
        title: 'Frequency',
        dataIndex: 'count',
        key: 'count',
    }
];

const columnsComment = [
    {
        title: 'User email',
        dataIndex: 'user',
        key: 'user',
    },
    {
        title: 'Answer content',
        dataIndex: 'value',
        key: 'value',
    }
];

const TabSurveyResult = ({ slug }) => {
    const dispatch = useDispatch()
    const { statistics, loadingSurvey } = useSelector((state) => state.survey)
    const [type, setType] = useState("Bar")

    useEffect(() => {
        handleGetStatistics(1, 1)
    }, [slug]);

    const handleGetStatistics = (page, size) => {
        let params = {
            id: slug,
            page: page,
            page_size: size
        }
        dispatch(fetchGetSurveyStatistics(params))
    }

    const handleChange = (value) => {
        setType(value);
    };

    const SetStatData = (statistics) => {
        const newArray = statistics.map(({ value, count }) => ([value, count]));
        const statArr = [
            ['question option', 'frequency'],
            ...newArray
        ]
        return statArr;
    }

    const renderStatistics = (item) => {
        if (item.question_type != "Comment") {
            return (
                <div>
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
                    {type == 'table' ? (
                        <div>
                            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}>
                                <b>{item.question}</b>
                                <b>{item.question_type}</b>
                            </div>
                            <Table
                                size='middle'
                                dataSource={item.statistics}
                                columns={columns}
                                pagination={false}
                            />
                        </div>
                    ) : (
                        <div>
                            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}>
                                <b>{item.question}</b>
                                <b>{item.question_type}</b>
                            </div>

                            <Chart
                                chartType={type}
                                data={SetStatData(item.statistics)}
                                width={"100%"}
                                height={"400px"}
                            />
                        </div>
                    )}
                </div>
            )
        } else {
            return (
                <div>
                    <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}>
                        <b>{item.question}</b>
                        <b>{item.question_type}</b>
                    </div>
                    <Table
                        size='middle'
                        dataSource={item.statistics}
                        columns={columnsComment}
                        pagination={false}
                    />
                </div>
            )
        }

    }

    return (
        <div>
            {statistics?.data?.map((item, index) => (
                <div key={index}>
                    {renderStatistics(item)}
                </div>
            ))}
            <Pagination
                defaultCurrent={1}
                total={statistics?.total}
                pageSize={1}
                onChange={(page) => handleGetStatistics(page, 1)}
                style={{ marginTop: '30px', float: 'right' }}
            />
        </div>
    );
};

export default TabSurveyResult;