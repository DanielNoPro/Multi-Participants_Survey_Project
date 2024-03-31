'use client'
import TabSurveyParticipant from '@/components/survey/TabSurveyParticipant';
import TabSurveyQuestion from '@/components/survey/TabSurveyQuestion';
import TabSurveyResult from '@/components/survey/TabSurveyResult';
import { fetchGetSurveyDetail } from '@/redux/slices/surveySlice';
import { Button, Tabs } from 'antd';
import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import {
    ArrowLeftOutlined
} from '@ant-design/icons';

const SurveyDetail = ({ params }) => {
    const { slug } = params
    const { surveyDetail } = useSelector((state) => state.survey)
    const dispatch = useDispatch()
    const router = useRouter()

    useEffect(() => {
        dispatch(fetchGetSurveyDetail(slug))
    }, [slug])

    const onChange = (key) => {
        // console.log(key);
    };

    const items = [
        {
            label: 'Participant',
            key: 'participant',
            children: <TabSurveyParticipant slug={slug} />,
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
                <Button shape="circle" icon={<ArrowLeftOutlined />} style={{float: "left"}} onClick={() => router.push(`/dashboard/survey`)} />
                <b>{surveyDetail.title}</b>
            </div>

            <Tabs
                defaultActiveKey="participant"
                centered
                items={items}
                onChange={onChange}
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