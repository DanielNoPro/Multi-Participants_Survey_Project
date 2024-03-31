'use client'
import React, { useState, useEffect } from 'react'
import { Button, Dropdown, Input, message, Modal, Table } from 'antd';
import {
    DeleteOutlined,
    EditOutlined,
    SendOutlined,
    CopyOutlined,
    MenuOutlined
} from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { fetchDeleteSurvey, fetchGetSurveys, setCurrentPage, setModalSurvey } from '@/redux/slices/surveySlice';
import SurveyModal from '@/components/survey/SurveyModal';
import { surveyService } from '@/services/surveyService';
const { Search } = Input;
import moment from 'moment';
import { useRouter } from 'next/navigation';
import { ReactMultiEmail } from 'react-multi-email';
import 'react-multi-email/dist/style.css';
import styles from './styles.module.css'

const SurveyPage = () => {
    const { surveys, loadingSurvey, current } = useSelector((state) => state.survey)
    const dispatch = useDispatch()
    const [dataSurvey, setDataSurvey] = useState({})
    const [isUpdate, setIsUpdate] = useState(false)
    const [sendModal, setSendModal] = useState(false)
    const [idSurvey, setIdSurvey] = useState(null)
    const [emails, setEmails] = useState([]);
    const [focused, setFocused] = useState(false);
    const [messageApi, contextHolder] = message.useMessage();

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

    const deleteSurvey = async (id) => {
        await dispatch(fetchDeleteSurvey(id))
        if (surveys.total > 1) {
            if ((current - 1) * 10 == surveys.total - 1) {
                handleGetSurveys(current - 1)
            } else {
                handleGetSurveys(current)
            }
        } else {
            handleGetSurveys(1)
        }
    };

    const handleGetSurveys = (page) => {
        dispatch(fetchGetSurveys(page))
        dispatch(setCurrentPage(page))
    }

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
                    trigger={['click']}
                >
                    <a onClick={(e) => {
                        e.stopPropagation()
                    }}>
                        <MenuOutlined />
                    </a>
                </Dropdown>
            ),
        }
    ];

    const handleAction = (key, record) => {
        switch (key) {
            case "delete":
                deleteSurvey(record?.id)
                break;
            case "edit":
                editSurvey(record?.id)
                break;
            case "invite":
                handleOpenSendModal(record?.id)
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
        dispatch(fetchGetSurveys(current))
    }, []);

    const handleOpenSendModal = (id) => {
        setIdSurvey(id)
        setSendModal(true)
    }
    const success = () => {
        messageApi.open({
            type: 'success',
            content: 'A login token has been sent to your emails.',
        });
        setEmails([])
        setSendModal(false)
    };

    const handleSend = () => {
        emails.forEach(async element => {
            const res = await surveyService.sendSurvey({
                email: element,
                tenant: 1,
                unit: 1,
                service: 1,
                survey: idSurvey
            })
            console.log(res);
        });
        success();
    }

    const handleCancelSend = () => {
        setEmails([])
        setSendModal(false)
    }

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
                rowClassName={styles.row}
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
                        dispatch(setCurrentPage(page))
                    },
                    current: current
                }}
            />
            {contextHolder}
            <Modal open={sendModal} closeIcon={null} destroyOnClose={true}
                footer={[
                    <Button key="back" onClick={handleCancelSend}>
                        Close
                    </Button>,
                    <Button key="submit" type="primary" onClick={handleSend}>
                        Send Invitation
                    </Button>
                ]}
            >
                <div style={{ textAlign: 'center', marginBottom: '10px', fontSize: '20px' }}>
                    <p>Emails</p>
                </div>
                <ReactMultiEmail
                    placeholder='Input your email then press "Enter"'
                    emails={emails}
                    onChange={(_emails) => {
                        setEmails(_emails);
                    }}
                    autoFocus={true}
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                    getLabel={(email, index, removeEmail) => {
                        return (
                            <div data-tag key={index}>
                                <div data-tag-item>{email}</div>
                                <span data-tag-handle onClick={() => removeEmail(index)}>
                                    X
                                </span>
                            </div>
                        );
                    }}
                />
            </Modal>
        </div>
    )
}

export default SurveyPage