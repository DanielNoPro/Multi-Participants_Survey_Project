'use client'
import TabSurveyQuestion from '@/components/survey/TabSurveyQuestion';
import TabSurveyResult from '@/components/survey/TabSurveyResult';
import { fetchGetSurveyDetail } from '@/redux/slices/surveySlice';
import { Tabs } from 'antd';
import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux';

const SurveyDetail = ({ params }) => {
    const { slug } = params
    const { surveyDetail } = useSelector((state) => state.survey)
    const dispatch = useDispatch()

    useEffect(() => {
        dispatch(fetchGetSurveyDetail(slug))
    }, [slug])

    const items = [
        {
            label: 'Participant',
            key: 'participant',
            children: <TabContent />,
        },
        {
            label: 'Question',
            key: 'question',
            children: <TabSurveyQuestion slug={slug} />,
        },
        {
            label: 'Result',
            key: 'result',
            children: <TabSurveyResult slug={slug} />,
        },
    ]

    return (
        <>
            <div style={{ textAlign: 'center', fontSize: '20px', color: '#5B9BD5' }}>
                <b>{surveyDetail.title}</b>
            </div>

            <Tabs
                defaultActiveKey="participant"
                centered
                items={items}
            />
        </>
    )
}

export default SurveyDetail

const TabContent = () => {
    return (
        <div>

        </div>
    )
}