'use client'
import { fetchCreateSurvey, fetchGetSurveys, fetchUpdateSurvey, setModalSurvey } from '@/redux/slices/surveySlice';
import { Button, Form, Input, Modal, DatePicker, Space, message } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
const { RangePicker } = DatePicker;
import React, { useEffect, useState } from 'react'
import { surveyService } from '@/services/surveyService';
import moment from 'moment';
import dayjs from 'dayjs';

const SurveyModal = ({ data, setData, isUpdate }) => {
    const dispatch = useDispatch()
    const {modalSurvey, current} = useSelector((state) => state.survey)
    const [messageApi, contextHolder] = message.useMessage();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setData({
            ...data,
            [name]: value,
        });
    };

    const handleChangeStart = (value, dateString) => {
        setData({
            ...data,
            start_date: value,
        });
    };

    const handleChangeEnd = (value, dateString) => {
        setData({
            ...data,
            end_date: value,
        });
    };

    const handleCancel = () => {
        dispatch(setModalSurvey(false));
        setData({})
    };

    const handleCreate = async () => {
        let formData = {
            title: data.title,
            description: data.description,
            start_date: new Date(data?.start_date).toISOString(),
            end_date: new Date(data?.end_date).toISOString(),
            is_active: true,
            survey_questions: []
        }
        // dispatch(fetchCreateSurvey(formData)).then(() => {
        //     dispatch(fetchGetSurveys(1));
        // });
        // dispatch(setModalSurvey(false))
        try {
            const res = await surveyService.createSurvey(formData);
            if (res) {
                dispatch(fetchGetSurveys(current));
                dispatch(setModalSurvey(false))
            }
        } catch (error) {
            messageApi.open({
                type: 'error',
                content: error.response.data.end_date,
            });
        }
    };

    const handleUpdate = async () => {
        let formData = {
            title: data?.title,
            description: data?.description,
            start_date: new Date(data?.start_date).toISOString(),
            end_date: new Date(data?.end_date).toISOString(),
            is_active: true,
            survey_questions: []
        }
        try {
            const res = await surveyService.updateSurvey(data.id, formData)
            if (res) {
                dispatch(fetchGetSurveys(current));
                dispatch(setModalSurvey(false))
            }
        } catch (error) {
            messageApi.open({
                type: 'error',
                content: error.response.data.end_date,
            });
        }
    }

    return (
        <Modal open={modalSurvey} closeIcon={null} destroyOnClose={true}
            footer={[
                <Button key="back" onClick={handleCancel}>
                    Close
                </Button>,
                <Button key="submit" type="primary" onClick={isUpdate ? handleUpdate : handleCreate}>
                    {isUpdate ? 'Update' : 'Create'}
                </Button>,
            ]}
        >
            {contextHolder}
            <div style={{ textAlign: 'center', marginBottom: '10px', fontSize: '20px' }}>
                {isUpdate
                    ? <p>
                        <span style={{ color: '#92CF69' }}>Edit</span> <span style={{ color: '#5B9BD5' }}>Survey</span>
                    </p>
                    : <p>
                        <span style={{ color: '#92CF69' }}>Create</span> <span style={{ color: '#5B9BD5' }}>Survey</span>
                    </p>}
            </div>
            <div>
                <Space direction="vertical" style={{ width: '100%' }}>
                    <Input name="title" placeholder="Survey name" value={data.title} onChange={handleChange} />
                    <Input name="description" placeholder="Survey description" value={data.description} onChange={handleChange} />
                    {isUpdate ? (
                        <>
                            <DatePicker
                                style={{ width: '100%' }}
                                placeholder="Start date"
                                value={dayjs(data.start_date, 'YYYY/MM/DD')}
                                format='YYYY/MM/DD'
                                onChange={handleChangeStart}
                            />
                            <DatePicker
                                style={{ width: '100%' }}
                                placeholder="End date"
                                value={dayjs(data.end_date, 'YYYY/MM/DD')}
                                format='YYYY/MM/DD'
                                onChange={handleChangeEnd}
                            />
                        </>
                    ) : (
                        <>
                            <DatePicker
                                style={{ width: '100%' }}
                                placeholder="Start date"
                                format='YYYY/MM/DD'
                                onChange={handleChangeStart}
                            />
                            <DatePicker
                                style={{ width: '100%' }}
                                placeholder="End date"
                                format='YYYY/MM/DD'
                                onChange={handleChangeEnd}
                            />
                        </>
                    )}
                </Space>
            </div>
        </Modal>
    )
}

export default SurveyModal