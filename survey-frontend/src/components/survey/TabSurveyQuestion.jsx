import { Button, Card, Input, message, Modal, Pagination, Select, Table } from 'antd';
import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import {
    DeleteOutlined,
    CloseOutlined
} from '@ant-design/icons';
import { fetchGetSurveyDetail, fetchGetSurveyQuestions, fetchGetQuestionSets, fetchGetSetPreConditions } from '@/redux/slices/surveySlice';
import { surveyService } from '@/services/surveyService';
import { fetchGetQuestions } from '@/redux/slices/questionSlice';
import { useRouter } from 'next/navigation';
import { questionService } from '@/services/questionService';

const TabSurveyQuestion = ({ slug }) => {
    const dispatch = useDispatch()
    const { sets, setConditions, loadingSurvey } = useSelector((state) => state.survey)
    const { questions, loadingQuestion } = useSelector((state) => state.question)
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isLogicOpen, setIsLogicOpen] = useState(false);
    const [current, setCurrent] = useState(1);
    const [currentSet, setCurrentSet] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [currentSetContent, setCurrentSetContent] = useState([]);
    const [questionOptions, setQuestionOptions] = useState([]);
    const [messageApi, contextHolder] = message.useMessage();
    const [condition, setCondition] = useState({
        logical_operator: "",
        survey_question: "",
        value: "",
        operator: ""
    });
    const [errorCondition, setErrorCondition] = useState("");

    const success = () => {
        messageApi.open({
            type: 'success',
            content: 'Add question to set successfully',
        });
    };

    const error = (err) => {
        messageApi.open({
            type: 'error',
            content: err,
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
                <>
                    <Button danger icon={<DeleteOutlined />} onClick={() => removeSurveyQuestion(slug, record.set, record.id)} />
                </>
            ),
        }
    ];

    const handleOpenLogic = async (set) => {
        let params = {
            survey_id: slug,
            set_id: set.id
        }
        dispatch(fetchGetSetPreConditions(params))
        setCurrentSetContent(set)
        setIsLogicOpen(true)
        getQuestionOfPreviousSet(set?.id)
    }

    const getQuestionOfPreviousSet = (currentSetId) => {
        const previousSets = sets.data.filter(s => s.id < currentSetId);
        const questions = []
        previousSets.forEach(set => {
            set.survey_question.forEach(surveyQuestion => {
                questions.push({
                    value: surveyQuestion.id,
                    label: surveyQuestion.question.content
                });
            });
        });
        setQuestionOptions(questions)
    }

    const handleCancelLogic = () => {
        setIsLogicOpen(false)
    }

    const handleSaveLogic = async (set_id) => {
        if (condition.logical_operator == "" || condition.operator == "" || condition.survey_question == "" || condition.value == "") {
            setErrorCondition("Required field is missing, please try again!")
        } else {
            await surveyService.createSetPreConditions(slug, set_id, condition)
            setCondition({
                logical_operator: "",
                survey_question: "",
                value: "",
                operator: ""
            })
            setIsLogicOpen(false)
        }
    }

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
                    Add to Set
                </Button>
            ),
        }
    ];

    const removeSurveyQuestion = async (survey_id, set_id, question_id) => {
        try {
            await questionService.removeQuestionFromSet(survey_id, set_id, question_id);
            handleGetSets(1)
        } catch (error) {
            messageApi.open({
                type: 'error',
                content: error.response.data[0],
            });
        }
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

    const openAddQuestionModal = (set_id) => {
        dispatch(fetchGetQuestions({ page: 1, size: 6 }))
        setIsModalOpen(true)
        setCurrentSet(set_id)
        setCurrentPage(1)
    }

    const addQuestionToSurvey = async (id) => {
        let data = {
            is_active: true,
            set: currentSet,
            survey: slug,
            question: id,
            asked_by: 1
        }
        try {
            await questionService.addQuestionToSet(slug, currentSet, data)
            success()
            handleGetSets(current)
        } catch (err) {
            error(err.response.data.non_field_errors[0])
        }
    }

    function handleCancel() {
        setIsModalOpen(false)
    }

    const createQuestionSet = async () => {
        const data = {
            is_active: true,
            survey: slug,
            set_created_by: 1
        }
        await surveyService.createQuestionSet(slug, data)
        handleGetSets(current)
    }

    const handleGetSets = (page) => {
        let params = {
            id: slug,
            page: page,
            size: 99
        }
        dispatch(fetchGetQuestionSets(params));
        setCurrent(page)
    }

    const deleteSet = async (set_id) => {
        await surveyService.deleteQuestionSet(slug, set_id)
        handleGetSets(current)
    }

    const deletePreCondition = async (id) => {
        await surveyService.deleteSetPreCondition(slug, currentSetContent?.id, id)
        dispatch(fetchGetSetPreConditions({
            survey_id: slug,
            set_id: currentSetContent?.id
        }))
    }

    const renderCondition = () => {
        if (setConditions?.length > 0) {
            return (
                setConditions.map((condition, index) => (
                    <div key={condition.id} style={{ display: 'flex', gap: "15px", justifyContent: 'end', marginBottom: '10px' }}>
                        <Select
                            disabled
                            style={{
                                width: 150,
                            }}
                            value={condition.logical_operator}
                            options={[
                                {
                                    value: 'AND',
                                    label: 'And',
                                },
                                {
                                    value: 'OR',
                                    label: 'Or',
                                },
                                {
                                    value: 'NOT',
                                    label: 'Not',
                                },
                            ]}
                        />
                        <Select
                            disabled
                            style={{
                                width: 200,
                            }}
                            value={condition.survey_question}
                            options={questionOptions}
                        />
                        <Select
                            disabled
                            style={{
                                width: 100,
                            }}
                            value={condition.operator}
                            options={[
                                {
                                    value: 'EQ',
                                    label: '=',
                                },
                                {
                                    value: 'LTE',
                                    label: '<=',
                                },
                                {
                                    value: 'GTE',
                                    label: '>=',
                                },
                                {
                                    value: 'LT',
                                    label: '<',
                                },
                                {
                                    value: 'GT',
                                    label: '>',
                                },
                                {
                                    value: 'IN',
                                    label: 'In',
                                },
                                {
                                    value: 'NIN',
                                    label: 'Not In',
                                },
                            ]}
                        />
                        <Input style={{ width: 200 }} value={condition.value} disabled />
                        <Button
                            type="primary"
                            shape="circle"
                            icon={<CloseOutlined />}
                            danger
                            onClick={() => deletePreCondition(condition.id)}
                        />
                    </div>
                ))
            )
        }
    }

    const handleChangeCondition = (name, value) => {
        setCondition(state => ({ ...state, [name]: value }));
    }

    const handleChangeConditionValue = (e) => {
        setCondition(state => ({ ...state, value: e.target.value }));
    }

    const handlePaginateQuestionModal = (page) => {
        dispatch(fetchGetQuestions({ page: page, size: 6 }))
        setCurrentPage(page)
    }

    useEffect(() => {
        handleGetSets(1)
    }, []);
    return (
        <div>
            {contextHolder}
            <Button type="primary" onClick={createQuestionSet} className="mb-10">Create Set Of Question</Button>
            {sets?.data?.map((set, index) => (
                <Card
                    key={set.id}
                    title={<div style={{ color: '#F24822' }}>{set.id}</div>}
                    extra={
                        <div style={{ display: "flex", gap: '5px' }}>
                            {index != sets.total - 1
                                && <Button style={{ backgroundColor: "#92CF69", color: 'white' }} onClick={() => handleOpenLogic(set)}>
                                    Precondition
                                </Button>
                            }
                            <Button style={{ backgroundColor: "#5B9BD5", color: 'white' }} onClick={() => openAddQuestionModal(set.id)}>
                                Add Question
                            </Button>
                            {index != sets.total - 1
                                && <Button onClick={() => deleteSet(set.id)}>Delete</Button>
                            }
                        </div>
                    }
                    style={{ marginBottom: "10px" }}
                    bodyStyle={{ padding: 0 }}
                >
                    <Table
                        size='middle'
                        columns={columns}
                        dataSource={set.survey_question}
                        rowKey={(record) => record.id}
                        pagination={false}
                    />
                </Card>
            ))}
            <Modal open={isModalOpen} closeIcon={null}
                footer={[
                    <Button key="back" onClick={handleCancel}>
                        Close
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
                        total: questions.total,
                        onChange: (page) => {
                            handlePaginateQuestionModal(page)
                        },
                        showSizeChanger: false,
                        current: currentPage
                    }}
                />
            </Modal>
            <Modal open={isLogicOpen} closeIcon={null} width={1000}
                footer={[
                    <Button key="cancel" onClick={handleCancelLogic}>
                        Close
                    </Button>,
                    <Button style={{ backgroundColor: "#92CF69" }} key="save" type="primary" onClick={() => handleSaveLogic(currentSetContent?.id)}>
                        Set Precondition
                    </Button>,
                ]}
            >
                <div style={{ textAlign: 'center', marginBottom: '10px', fontSize: '20px', display: 'flex', justifyContent: 'center' }}>
                    <p style={{ border: '0.5px solid black', borderRadius: "10px", color: '#F24822', width: '50%' }}>{currentSetContent?.id}</p>
                </div>
                <div style={{ color: "#92CF69", marginBottom: '20px' }}>Display This Set Of Question If</div>
                {renderCondition()}
                <div style={{ display: 'flex', gap: "15px", justifyContent: 'end' }}>
                    <Select
                        style={{
                            width: 150,
                        }}
                        value={condition.logical_operator}
                        onChange={(e) => handleChangeCondition("logical_operator", e)}
                        options={[
                            {
                                value: 'AND',
                                label: 'And',
                            },
                            {
                                value: 'OR',
                                label: 'Or',
                            },
                            {
                                value: 'NOT',
                                label: 'Not',
                            },
                        ]}
                    />
                    <Select
                        style={{
                            width: 200,
                        }}
                        value={condition.survey_question}
                        onChange={(e) => handleChangeCondition("survey_question", e)}
                        options={questionOptions}
                    />
                    <Select
                        style={{
                            width: 100,
                        }}
                        value={condition.operator}
                        onChange={(e) => handleChangeCondition("operator", e)}
                        options={[
                            {
                                value: 'EQ',
                                label: '=',
                            },
                            {
                                value: 'LTE',
                                label: '<=',
                            },
                            {
                                value: 'GTE',
                                label: '>=',
                            },
                            {
                                value: 'LT',
                                label: '<',
                            },
                            {
                                value: 'GT',
                                label: '>',
                            },
                            {
                                value: 'IN',
                                label: 'In',
                            },
                            {
                                value: 'NIN',
                                label: 'Not In',
                            },
                        ]}
                    />
                    <Input value={condition.value} style={{ width: 200 }} onChange={handleChangeConditionValue} />
                    <Button
                        style={{ opacity: 0 }}
                        type="primary"
                        shape="circle"
                        icon={<CloseOutlined />}
                        danger
                    />
                </div>
                <div style={{ display: 'flex', gap: "15px", justifyContent: 'end' }}>
                    <p style={{ color: 'red' }}>{errorCondition}</p>
                </div>
            </Modal>
        </div>
    )
}

export default TabSurveyQuestion