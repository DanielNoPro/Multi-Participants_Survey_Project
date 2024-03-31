'use client'
import { Button, Card, Checkbox, Input, Select, Space, message, notification } from 'antd'
import Layout, { Content, Footer, Header } from 'antd/es/layout/layout'
import React, { useEffect, useState, useMemo } from 'react'
import moment from 'moment';
import { useDispatch, useSelector } from 'react-redux';
import { fetchGetUserSurveyQuestions } from '@/redux/slices/surveySlice'
import styles from './styles.module.css'
import Likert from 'react-likert-scale';
import { apiUser } from '@/constants/api';
import Image from 'next/image';
import { surveyService } from '@/services/surveyService';
import { useRouter } from 'next/navigation';

const Context = React.createContext({
    name: 'Default',
});

export default function Page({ params }) {
    const [start, setStart] = useState(false)
    const [data, setData] = useState([])
    const [isLate, setIsLate] = useState(false)
    const [excludeSets, setExcludeSets] = useState([])
    const [questions, setQuestions] = useState([])
    const [currentSetId, setCurrentSetId] = useState("")
    const [isSubmit, setIsSubmit] = useState(false)
    const { slug } = params
    const dispatch = useDispatch()
    const { userSurvey, loadingSurvey, surveyErrors } = useSelector((state) => state.survey)
    const router = useRouter()

    const [api, contextHolder] = notification.useNotification();

    function handleStartSurvey() {
        if(surveyErrors == "Participant is deactivated"){
            router.push(`/surveys/revoke`)
        } else {
            setStart(true)
        }
    }

    useEffect(() => {
        dispatch(fetchGetUserSurveyQuestions({ token: decodeURIComponent(slug[1]) }))
            .then(res => {
                setQuestions(res.payload?.survey?.question_sets[0].survey_question)
                setExcludeSets([res.payload.survey.id])
                setCurrentSetId(res.payload.survey?.question_sets[0].id)
                const newArray = res.payload?.survey?.question_sets[0].survey_question.map((item, index) => {
                    if (item.question.question_type.name == "Comment") {
                        return { question: item.question.id, answer: { content: '' } };
                    } else {
                        return { question: item.question.id, answer: { options: [] } };
                    }
                });
                setData(newArray);
                let now = new Date();
                let end = new Date(res.payload?.survey?.end_date);
                if (+end < +now) {
                    setIsLate(true)
                }
            })
    }, [])

    const handleChangeLikert = (answer, index) => {
        updateState(index, [answer.value]);
    }

    const handleChangeMC = (answer, index) => {
        updateState(index, answer);
    };

    const handleChangeComment = (e, index) => {
        let question = [...data]
        question[index].answer.content = e.target.value;
        setData(question)
    }

    const updateState = (index, newAnswer) => {
        setData((prevQuestions) =>
            prevQuestions.map((question, i) =>
                i === index ? { ...question, answer: { options: newAnswer } } : question
            )
        );
    };

    const handleChangeDropdown = (value, index) => {
        updateState(index, [value]);
    }

    function handleSubmit() {
        apiUser.post(`/api/v1/surveys/${slug[0]}/submit/`, { data: data }, {
            headers: {
                Authorization: `Token ${userSurvey.token}`
            }
        }).then((res) => {
            router.push(`/surveys/submission`)
        })
    }

    const handleNext = async () => {
        let payload = {
            data: {
                exclude_sets: excludeSets,
                items: data
            }
        }
        try {
            const res = await surveyService.getNextSet(slug[0], currentSetId, payload)
            setCurrentSetId(res.id)
            setExcludeSets([...excludeSets, res.id])
            const newArray = res.survey_question?.map((item, index) => {
                if (item.question.question_type.name == "Comment") {
                    return { question: item.question.id, answer: { content: '' } };
                } else {
                    return { question: item.question.id, answer: { options: [] } };
                }
            });
            setData(state => [...state, ...newArray])
            setQuestions(state => [...state, ...res.survey_question])
        } catch (error) {
            setIsSubmit(true)
        }
    }

    const renderOptions = (question, index) => {
        switch (question?.question_type?.name) {
            case "Comment":
                return (
                    <Input onChange={(e) => handleChangeComment(e, index)} />
                )
            case "Multiple Choice":
                return (
                    <div className={styles.antCheckbox}
                    >
                        <Checkbox.Group onChange={(answer) => handleChangeMC(answer, index)}>
                            <Space direction="vertical">
                                {question?.options.map((item, index) => (
                                    <Checkbox key={item.id} value={item.id}>{item.content}</Checkbox>
                                ))}
                            </Space>
                        </Checkbox.Group>
                    </div>
                )
            case "Likert":
                return (
                    <Likert
                        id={question.id}
                        responses={question?.options.map((item) => ({
                            value: item.id,
                            text: item.content
                        }))}
                        onChange={(answer) => handleChangeLikert(answer, index)}
                    />
                )
            case "Dropdown":
                return (
                    <Select
                        style={{ width: '100%' }}
                        options={question?.options.map((item) => ({
                            value: item.id,
                            label: item.content
                        }))}
                        onChange={(answer) => handleChangeDropdown(answer, index)}
                    />
                )
            default:
                break;
        }
    }

    const renderSurvey = () => {
        if (isLate) {
            return (
                <Layout>
                    <Header
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            background: 'white',
                            padding: '50px 0'
                        }}
                    >
                        <Image src="/images/logo.png" alt="logo" style={{ padding: '20px' }} width={300}
                            height={200}
                            sizes="100vw" />
                    </Header>
                    <Content
                        style={{
                            padding: '0 100px',
                            background: 'white'
                        }}
                    >
                        <div
                            style={{
                                minHeight: 480,
                                padding: 24,
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center'
                            }}
                        >
                            <div>
                                <p style={{ color: '#1BB12A', fontSize: '18px', fontWeight: '500' }}>This Survey has passed the due date</p>
                            </div>
                        </div>
                    </Content>
                </Layout>
            )
        } else {
            if (start) {
                return (
                    <>
                        {contextHolder}
                        <Layout>
                            <Header
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    background: 'white',
                                    padding: '50px 0'
                                }}
                            >
                                <Image src="/images/logo.png" alt="logo" style={{ padding: '20px' }} width={300}
                                    height={200}
                                    sizes="100vw" />
                            </Header>
                            <div className={styles.submit_section}>
                                <Card
                                    style={{
                                        width: 300,
                                    }}
                                >
                                    <p style={{ fontSize: '15px', fontWeight: '500', margin: '10px 0' }}>Start date: {moment(userSurvey?.survey?.start_date).format("YYYY/MM/DD ")}</p>
                                    <p style={{ fontSize: '15px', fontWeight: '500', marginBottom: '10px' }}>End date: {moment(userSurvey?.survey?.end_date).format("YYYY/MM/DD ")}</p>
                                    {isSubmit
                                        ? <Button type='primary' onClick={handleSubmit}>Submit</Button>
                                        : <Button style={{ backgroundColor: "#92CF69", color: 'white' }} type='primary' onClick={handleNext}>Next</Button>
                                    }
                                </Card>
                            </div>
                            <Content
                                style={{
                                    padding: '0 25%',
                                    background: 'white'
                                }}
                            >
                                <p style={{ color: '#5B9BD5', fontSize: '48px', textAlign: 'center' }}>{userSurvey?.survey?.title}</p>
                                <div>
                                    {questions?.map((item, index) => (
                                        <div className={styles.question} key={item.id}>
                                            <div className={styles.question_title}>
                                                <span style={{ fontWeight: '600' }}>Question {index + 1}</span>:    {item.question.content}
                                            </div>
                                            {renderOptions(item.question, index)}
                                        </div>
                                    ))
                                    }
                                </div>
                            </Content>
                        </Layout>
                    </>
                )
            }
            return (
                <Layout>
                    <Header
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            background: 'white',
                            padding: '50px 0'
                        }}
                    >
                        <Image src="/images/logo.png" alt="logo" style={{ padding: '20px' }} width={300}
                            height={200}
                            sizes="100vw" />
                    </Header>
                    <Content
                        style={{
                            padding: '0 100px',
                            background: 'white'
                        }}
                    >
                        <div
                            style={{
                                minHeight: 480,
                                padding: 24,
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center'
                            }}
                        >
                            <div>
                                <p style={{ color: '#5B9BD5', fontSize: '48px', textAlign: 'center' }}>{userSurvey?.survey?.title}</p>
                                <p style={{ color: '#1BB12A', fontSize: '18px', fontWeight: '500' }}>{userSurvey?.survey?.description}</p>
                                <p style={{ fontSize: '15px', fontWeight: '500', margin: '10px 0' }}>Start date: {moment(userSurvey?.survey?.start_date).format("YYYY/MM/DD ")}</p>
                                <p style={{ fontSize: '15px', fontWeight: '500' }}>End date: {moment(userSurvey?.survey?.end_date).format("YYYY/MM/DD ")}</p>
                                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                                    <Button type='primary' onClick={handleStartSurvey}>Start Survey</Button>
                                </div>
                            </div>
                        </div>
                    </Content>
                </Layout>
            )
        }
    }

    return (
        <div>
            {renderSurvey()}
        </div>
    )
}
