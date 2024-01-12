'use client'
import React, { useState, useEffect, useRef } from 'react'
import { Button, DatePicker, Dropdown, Input, Modal, Table } from 'antd';
import {
    DeleteOutlined,
    EditOutlined,
    SendOutlined,
    CopyOutlined,
    BorderOuterOutlined
} from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCreateSurvey, fetchDeleteSurvey, fetchGetSurveys, setModalSurvey } from '@/redux/slices/surveySlice';
import SurveyModal from '@/components/survey/SurveyModal';
import { surveyService } from '@/services/surveyService';
const { Search } = Input;
import moment from 'moment';
import { useRouter } from 'next/navigation';



const SurveyPage = () => {
    const { surveys, loadingSurvey } = useSelector((state) => state.survey)
    const dispatch = useDispatch()
    const [dataSurvey, setDataSurvey] = useState({})
    const [isUpdate, setIsUpdate] = useState(false)
    const router = useRouter()

    const createSurvey = () => {
        setDataSurvey({})
        setIsUpdate(false)
        dispatch(setModalSurvey(true))
    };

    const editSurvey = async (id) => {
        const res = await surveyService.getSurveyDetail(id)
        setDataSurvey(res);
        dispatch(setModalSurvey(true))
        setIsUpdate(true)
    };

    const items = [
        {
            label: 'Delete',
            key: 'delete',
            icon: <DeleteOutlined />,
        },
        {
            label: 'Edit',
            key: 'edit',
            icon: <EditOutlined />,
        },
        {
            label: 'Send Invitation',
            key: 'invite',
            icon: <SendOutlined />,
        },
        {
            label: 'Duplicate',
            key: 'duplicate',
            icon: <CopyOutlined />,
        },
    ];

    const columns = [
        {
            title: 'Survey name',
            dataIndex: 'title',
            key: 'title',
        },
        {
            title: 'Start Date',
            dataIndex: 'start_date',
            key: 'start_date',
            render: (text) => {
                return (
                    <div>
                        <p>{moment(text).format("YYYY/MM/DD")}</p>
                    </div>
                );
            },
        },
        {
            title: 'End Date',
            dataIndex: 'end_date',
            key: 'end_date',
            render: (text) => {
                return (
                    <div>
                        <p>{moment(text).format("YYYY/MM/DD")}</p>
                    </div>
                );
            },
        },
        {
            title: '',
            key: 'action',
            render: (_, record) => (
                <Dropdown
                    menu={{
                        items,
                        onClick: ({ key, domEvent }) => {
                            handleAction(key, record);
                            domEvent.stopPropagation()
                        }
                    }}
                >
                    <a onClick={(e) => {
                        e.stopPropagation()
                    }}>
                        <BorderOuterOutlined />
                    </a>
                </Dropdown>
            ),
        }
    ];

    const handleAction = (key, record) => {
        switch (key) {
            case "delete":
                dispatch(fetchDeleteSurvey(record?.id))
                    .then(() => dispatch(fetchGetSurveys(1)))
                break;
            case "edit":
                editSurvey(record?.id)
                break;
            case "invite":
                // onClickFunction()
                break;
            case "duplicate":
                duplicateSurvey(record?.id)
                break;
            default:
                break;
        };
    }

    const duplicateSurvey = async (id) => {
        const res = await surveyService.duplicateSurvey(id);
        if (res) {
            dispatch(fetchGetSurveys(1))
        }
    }

    useEffect(() => {
        dispatch(fetchGetSurveys(1))
    }, []);

    return (
        <div>
            {/* <Search enterButton className="mb-20" /> */}
            <Button type="primary" onClick={createSurvey} className="mb-10">Create Survey</Button>
            <SurveyModal data={dataSurvey} setData={setDataSurvey} isUpdate={isUpdate} />
            <Table
                loading={loadingSurvey}
                size='middle'
                columns={columns}
                dataSource={surveys.data}
                rowKey={(record) => record.id}
                onRow={(record, rowIndex) => {
                    return {
                        onClick: (event) => {
                            router.push(`/dashboard/survey/${record.id}`)
                        },
                    };
                }}
                pagination={{
                    pageSize: 10,
                    total: surveys.total,
                    onChange: (page) => {
                        dispatch(fetchGetSurveys(page))
                    },
                }}
            />
        </div>
    )
}

export default SurveyPage