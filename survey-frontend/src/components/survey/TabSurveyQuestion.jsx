import { Button, message, Modal, Table } from 'antd';
import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import {
    DeleteOutlined,
    ArrowLeftOutlined
} from '@ant-design/icons';
import { fetchGetSurveyDetail, fetchGetSurveyQuestions } from '@/redux/slices/surveySlice';
import { surveyService } from '@/services/surveyService';
import { fetchGetQuestions } from '@/redux/slices/questionSlice';
import { useRouter } from 'next/navigation';

const TabSurveyQuestion = ({ slug }) => {
    const dispatch = useDispatch()
    const { surveyQuestions, loadingSurvey } = useSelector((state) => state.survey)
    const { questions, loadingQuestion } = useSelector((state) => state.question)
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [messageApi, contextHolder] = message.useMessage();
    const router = useRouter()

    const success = () => {
        messageApi.open({
            type: 'success',
            content: 'Add question to survey successfully',
        });
    };

    const columns = [
        {
            title: 'Question',
            dataIndex: 'question',
            key: 'question',
            render: (record) => (
                <div>{record.content}</div>
            ),
        },
        {
            title: 'Type',
            dataIndex: 'question',
            key: 'question',
            render: (record) => (
                <div>{record.question_type.name}</div>
            ),
        },
        {
            title: '',
            key: 'action',
            render: (_, record) => (
                <Button danger icon={<DeleteOutlined />} onClick={() => removeSurveyQuestion(slug, record.id)} />
            ),
        }
    ];

    const columnsQuestion = [
        {
            title: 'Question',
            dataIndex: 'content',
            key: 'content',
        },
        {
            title: 'Type',
            dataIndex: 'question_type',
            key: 'question_type',
            render: (text) => (
                <div>{renderQuestionType(text)}</div>
            ),
        },
        {
            title: "",
            key: 'action',
            render: (_, record) => (
                <Button type="primary" onClick={() => addQuestionToSurvey(record.id)}>
                    Add to Survey
                </Button>
            ),
        }
    ];

    const removeSurveyQuestion = async (survey_id, question_id) => {
        await surveyService.removeSurveyQuestion(survey_id, question_id);
        handleGetSurveyQuestions(1)
    }

    const renderQuestionType = (type) => {
        switch (type) {
            case 1:
                return <p>Comment</p>
            case 2:
                return <p>Multiple Choice</p>
            case 3:
                return <p>Likert</p>
            case 4:
                return <p>Dropdown</p>
            default:
                break;
        }
    }

    const handleGetSurveyQuestions = (page) => {
        let params = {
            id: slug,
            page: page
        }
        dispatch(fetchGetSurveyQuestions(params));
    }

    const openAddQuestionModal = () => {
        dispatch(fetchGetQuestions({ page: 1, size: 7 }))
        setIsModalOpen(true)
    }

    const addQuestionToSurvey = async (id) => {
        let data = {
            is_active: true,
            survey: Number(slug),
            question: id,
            asked_by: 1
        }
        const res = await surveyService.addQuestionToSurvey(slug, data)
        if (res) {
            success()
            handleGetSurveyQuestions(1)
        }
    }

    function handleCancel() {
        setIsModalOpen(false)
    }

    useEffect(() => {
        handleGetSurveyQuestions(1)
    }, []);

    return (
        <div>
            {contextHolder}
            <Button shape="circle" icon={<ArrowLeftOutlined />} onClick={() => router.push(`/dashboard/survey`)} />
            <Button type="primary" onClick={openAddQuestionModal} className="mb-10">Add Questions</Button>
            <Table
                size='middle'
                loading={loadingSurvey}
                columns={columns}
                dataSource={surveyQuestions.data}
                rowKey={(record) => record.id}
                pagination={{
                    pageSize: 6,
                    // total: surveyQuestions.total,
                    onChange: (page) => {
                        handleGetSurveyQuestions(page)
                    },
                }}
            />
            <Modal open={isModalOpen} closeIcon={null}
                footer={[
                    <Button key="back" onClick={handleCancel}>
                        Cancel
                    </Button>
                ]}
            >
                <div style={{ textAlign: 'center', marginBottom: '10px', fontSize: '20px' }}>
                    <p>Question List</p>
                </div>
                <Table
                    size='middle'
                    loading={loadingQuestion}
                    columns={columnsQuestion}
                    dataSource={questions.data}
                    rowKey={(record) => record.id}
                    pagination={{
                        pageSize: 6,
                        // total: questions.total,
                        onChange: (page) => {
                            dispatch(fetchGetQuestions({ page: page, size: 6 }))
                        },
                    }}
                />
            </Modal>
        </div>
    )
}

export default TabSurveyQuestion