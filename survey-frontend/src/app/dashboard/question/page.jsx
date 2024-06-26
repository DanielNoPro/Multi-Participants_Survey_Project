'use client'
import { fetchGetQuestions, fetchGetQuestionTypes, setCurrentPage, setModalQuestion } from '@/redux/slices/questionSlice';
import { Button, Dropdown, Table } from 'antd'
import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import {
    DeleteOutlined,
    EditOutlined,
    MenuOutlined,
    LockOutlined,
    LockTwoTone
} from '@ant-design/icons';
import QuestionModal from '@/components/question/QuestionModal';
import { questionService } from '@/services/questionService';

const initialData = {
    content: "",
    is_active: true,
    question_type: "",
    question_created_by: 1,
    options: [
        {
            content: "",
            is_active: true
        },
    ],
}

const Page = () => {
    const { questions, loading, current } = useSelector((state) => state.question)
    const dispatch = useDispatch();
    const [dataQuestion, setDataQuestion] = useState(initialData)
    const [isUpdate, setIsUpdate] = useState(false)
    const [questionOptions, setQuestionOptions] = useState([])

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
    ];

    const columns = [
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
            title: '',
            key: 'action',
            render: (_, record) => (
                record.is_editable && record.is_deletable ? (
                    <Dropdown
                        menu={{
                            items,
                            onClick: ({ key }) => {
                                handleAction(key, record);
                            }
                        }}
                        trigger={['click']}
                    >
                        <a onClick={(e) => e.preventDefault()}>
                            <MenuOutlined />
                        </a>
                    </Dropdown>
                ) : (
                    <LockTwoTone twoToneColor="#FF0000" />
                )
            ),
        },
    ];

    const handleAction = (key, record) => {
        switch (key) {
            case "delete":
                deleteQuestion(record?.id)
                break;
            case "edit":
                editQuestion(record?.id)
                break;
            default:
                break;
        };
    }

    const deleteQuestion = (id) => {
        questionService.deleteQuestion(id).then(() => {
            if (questions.total > 1) {
                if ((current - 1) * 10 == questions.total - 1) {
                    handleGetQuestions(current - 1, 10)
                } else {
                    handleGetQuestions(current, 10)
                }
            } else {
                handleGetQuestions(1, 10)
            }
        })
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

    const editQuestion = async (id) => {
        const res1 = await questionService.getQuestionDetail(id);
        if (res1) {
            setDataQuestion(res1)
        }

        const res2 = await questionService.getQuestionOptions(id);
        if (res2) {
            setQuestionOptions(res2.data);
        }
        dispatch(setModalQuestion(true))
        dispatch(fetchGetQuestionTypes())
        setIsUpdate(true)
    }

    const resetOption = async (id) => {
        const res = await questionService.getQuestionOptions(id);
        if (res) {
            setQuestionOptions(res.data);
        }
    }

    useEffect(() => {
        const handleGetQuestions = async (page, size) => {
            let params = {
                page: page,
                size: size
            }
            await dispatch(fetchGetQuestions(params))
        }

        handleGetQuestions(1, 10)
    }, []);

    const createQuestion = async () => {
        setDataQuestion(initialData)
        setIsUpdate(false)
        dispatch(setModalQuestion(true))
        dispatch(fetchGetQuestionTypes())
    }

    const handleGetQuestions = (page, size) => {
        let params = {
            page: page,
            size: size
        }
        dispatch(fetchGetQuestions(params))
        dispatch(setCurrentPage(page))
    }

    return (
        <div>
            <Button type="primary" style={{ backgroundColor: "#5B9BD5" }} className="mb-10" onClick={createQuestion}>Create Question</Button>
            <QuestionModal
                data={dataQuestion}
                setData={setDataQuestion}
                questionOptions={questionOptions}
                setQuestionOptions={setQuestionOptions}
                initialData={initialData}
                isUpdate={isUpdate}
                resetOption={resetOption}
            />
            <Table
                loading={loading}
                columns={columns}
                size='middle'
                dataSource={questions.data}
                rowKey={(record) => record.id}
                pagination={{
                    pageSize: 10,
                    total: questions.total,
                    onChange: (page) => {
                        handleGetQuestions(page, 10)
                    },
                    current: current,
                    showSizeChanger: false
                }}
            />
        </div>
    )
}

export default Page

