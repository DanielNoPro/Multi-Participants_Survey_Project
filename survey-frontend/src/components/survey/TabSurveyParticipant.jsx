import { fetchGetSurveyParticipants } from '@/redux/slices/surveySlice';
import { surveyService } from '@/services/surveyService';
import { Button, message, Modal, Switch, Table } from 'antd';
import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux';

const TabSurveyParticipant = ({ slug }) => {
    const dispatch = useDispatch()
    const { participants, loadingSurvey } = useSelector((state) => state.survey)
    const [current, setCurrent] = useState(1)

    const columns = [
        {
            title: 'Email',
            key: 'email',
            render: (record) => (
                <div>{record?.participant.email}</div>
            ),
        },
        {
            title: 'Progress',
            dataIndex: 'status',
            key: 'status'
        },
        {
            title: 'Times submit',
            dataIndex: 'submit_count',
            key: 'submit_count'
        },
        {
            title: '',
            dataIndex: 'is_active',
            key: 'is_active',
            render: (e, record) => (
                <Switch value={record?.is_active} onChange={(checked) => onActivateSurvey(checked, record.id)} />
            ),
        }
    ];

    const onActivateSurvey = async (checked, id) => {
        if (checked) {
            await surveyService.activateSurvey(id)
            handleGetSurveyParticipants(current)
        } else {
            await surveyService.deactivateSurvey(id)
            handleGetSurveyParticipants(current)
        }
    };

    const handleGetSurveyParticipants = (page) => {
        let params = {
            id: slug,
            page: page
        }
        dispatch(fetchGetSurveyParticipants(params));
        setCurrent(page)
    }

    useEffect(() => {
        handleGetSurveyParticipants(1)
    }, []);
    const onChange = (checked) => {
        console.log(`switch to ${checked}`);
    };

    return (
        <div>
            <Switch defaultChecked onChange={onChange} style={{opacity:0}}/> 
            <Table
                size='middle'
                loading={loadingSurvey}
                columns={columns}
                dataSource={participants.data}
                rowKey={(record) => record.id}
                pagination={{
                    pageSize: 10,
                    total: participants.total,
                    onChange: (page) => {
                        handleGetSurveyParticipants(page)
                    },
                    current: current
                }}
            />
        </div>
    )
}

export default TabSurveyParticipant