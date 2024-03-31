'use client'
import { Button, Input, Modal, DatePicker, Select, Radio, Space } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import React, { useEffect, useState } from 'react'
import { fetchGetQuestions, setCurrentPage, setModalQuestion } from '@/redux/slices/questionSlice';
import { questionService } from '@/services/questionService';
import {
    PlusOutlined,
    MinusOutlined,
    EditOutlined,
    CheckOutlined,
    CloseOutlined
} from '@ant-design/icons';

const QuestionModal = ({ data, setData, isUpdate, initialData, questionOptions, setQuestionOptions, resetOption }) => {
    const dispatch = useDispatch()
    const { modalQuestion, questionTypes, current } = useSelector((state) => state.question)
    const [extraOptions, setExtraOptions] = useState({})

    const handleChange = (e) => {
        setData({
            ...data,
            content: e.target.value,
        });
    };

    const handleChangeSelect = (value) => {
        setData({
            ...data,
            question_type: value,
        });
    }

    const handleChangeOption = (e, index) => {
        setData(state => ({
            ...state,
            options: state.options.map((op, i) => {
                if (i === index) {
                    return { ...op, content: e.target.value }
                }

                return op
            })
        }))
    };

    const handleChangeEditOption = (e, id) => {
        setQuestionOptions(state => {
            const newState = state.map(op => {
                if (op.id == id) {
                    return { ...op, content: e.target.value };
                }
                return op;
            });

            return newState;
        })
    };

    const handleCancel = () => {
        dispatch(setModalQuestion(false));
        setData(initialData)
    };

    const handleCreate = async () => {
        if (data.question_type == 1) {
            let newData = {
                ...data,
                options: []
            }
            const res = await questionService.createQuestion(newData)
            if (res) {
                dispatch(fetchGetQuestions({ page: 1, size: 10 }));
            }
        } else {
            const res = await questionService.createQuestion(data)
            if (res) {
                dispatch(fetchGetQuestions({ page: 1, size: 10 }));
            }
        }
        dispatch(setModalQuestion(false))
        dispatch(setCurrentPage(current))
        setData(initialData)
    };

    const handleUpdate = async () => {
        let formData = new FormData()
        formData.append('content', data.content)
        const res = await questionService.updateQuestion(data.id, formData)
        if (res) {
            dispatch(fetchGetQuestions({ page: 1, size: 10 }));
            dispatch(setCurrentPage(current))
            dispatch(setModalQuestion(false))
        }
    }

    const removeEditOption = async (question_id, option_id) => {
        await questionService.deleteQuestionOption(question_id, option_id)
        resetOption(data?.id);
    }

    const updateOption = async (question_id, option_id) => {
        // console.log(question_id, option_id);
        // console.log(questionOptions.find(x => x.id == option_id));
        let newItem = questionOptions.find(x => x.id == option_id);
        let formData = new FormData()
        formData.append('content', newItem.content);
        formData.append('is_active', true);
        formData.append("question", question_id)
        await questionService.updateQuestionOption(question_id, option_id, formData);
    }

    const addExtraOptions = () => {
        setExtraOptions({
            content: "",
            is_active: true,
            question: data.id
        });
    }

    const handleChangeExtraOption = (e) => {
        setExtraOptions({
            ...extraOptions,
            content: e.target.value
        })
    };

    const createOptionQuestion = async () => {
        const res = await questionService.createQuestionOption(data.id, extraOptions);
        if (res) {
            resetOption(data.id)
            setExtraOptions({})
        }
    }

    const removeExtraOption = () => {
        setExtraOptions({});
    }

    const renderQuestionOption = (type) => {
        if (type == 1 || type == "") {
            return
        } else {
            if (isUpdate) {
                return (
                    <Space direction="vertical" style={{ width: '100%', marginTop: '10px' }}>
                        <Button type="primary" icon={<PlusOutlined />} onClick={addExtraOptions} disabled={questionOptions?.length > 5}>
                            Add Option
                        </Button>
                        {questionOptions.map((item, index) => {
                            return (
                                <div style={{ display: 'flex', gap: '5px' }} key={item.id}>
                                    <Input addonBefore="Option" value={item.content} onChange={(e) => handleChangeEditOption(e, item.id)} />
                                    <Button
                                        type="primary"
                                        shape="circle"
                                        icon={<EditOutlined />}
                                        onClick={() => updateOption(data.id, item.id)}
                                        style={{ backgroundColor: '#28a745' }}
                                    />
                                    <Button
                                        type="primary"
                                        shape="circle"
                                        icon={<MinusOutlined />}
                                        danger
                                        onClick={() => removeEditOption(data.id, item.id)}
                                    />
                                </div>
                            )
                        })}
                        {Object.keys(extraOptions).length > 0 ? (
                            <div style={{ display: 'flex', gap: '5px' }}>
                                <Input addonBefore="Extra" value={extraOptions?.content} onChange={handleChangeExtraOption} />
                                <Button
                                    type="primary"
                                    shape="circle"
                                    icon={<CheckOutlined />}
                                    onClick={createOptionQuestion}
                                    style={{ backgroundColor: '#28a745' }}
                                />
                                <Button
                                    type="primary"
                                    shape="circle"
                                    icon={<CloseOutlined />}
                                    danger
                                    onClick={removeExtraOption}
                                />
                            </div>
                        ) : (
                            <></>
                        )}
                    </Space>
                );
            } else {
                return (
                    <Space direction="vertical" style={{ width: '100%', marginTop: '10px' }}>
                        {data.options.map((item, index) => {
                            return (
                                <div style={{ display: 'flex', gap: '5px' }} key={index}>
                                    <Input addonBefore="Option" value={item.content} onChange={(e) => handleChangeOption(e, index)} />
                                    {index == 0 ?
                                        (
                                            <Button
                                                type="primary"
                                                shape="circle"
                                                icon={<PlusOutlined />}
                                                onClick={addOption}
                                                disabled={data?.options?.length > 5}
                                            />
                                        ) : (
                                            <Button
                                                type="primary"
                                                shape="circle"
                                                icon={<MinusOutlined />}
                                                danger
                                                onClick={() => removeOption(index)}
                                            />
                                        )
                                    }
                                </div>
                            )
                        })}
                    </Space>
                );
            }
        }
        // switch (type) {
        //     case 1:
        //         break;
        //     case 2: case 3:
        //         if (isUpdate) {
        //             return (
        //                 <Space direction="vertical" style={{ width: '100%', marginTop: '10px' }}>
        //                     <Button type="primary" icon={<PlusOutlined />} onClick={addExtraOptions}>
        //                         Add Option
        //                     </Button>
        //                     {questionOptions.map((item, index) => {
        //                         return (
        //                             <div style={{ display: 'flex', gap: '5px' }} key={item.id}>
        //                                 <Input addonBefore="Option" value={item.content} onChange={(e) => handleChangeEditOption(e, item.id)} />
        //                                 <Button
        //                                     type="primary"
        //                                     shape="circle"
        //                                     icon={<EditOutlined />}
        //                                     onClick={() => updateOption(data.id, item.id)}
        //                                     style={{ backgroundColor: '#28a745' }}
        //                                 />
        //                                 <Button
        //                                     type="primary"
        //                                     shape="circle"
        //                                     icon={<MinusOutlined />}
        //                                     danger
        //                                     onClick={() => removeEditOption(data.id, item.id)}
        //                                 />
        //                             </div>
        //                         )
        //                     })}
        //                     {Object.keys(extraOptions).length > 0 ? (
        //                         <div style={{ display: 'flex', gap: '5px' }}>
        //                             <Input addonBefore="Extra" value={extraOptions?.content} onChange={handleChangeExtraOption} />
        //                             <Button
        //                                 type="primary"
        //                                 shape="circle"
        //                                 icon={<CheckOutlined />}
        //                                 onClick={createOptionQuestion}
        //                                 style={{ backgroundColor: '#28a745' }}
        //                             />
        //                             <Button
        //                                 type="primary"
        //                                 shape="circle"
        //                                 icon={<CloseOutlined />}
        //                                 danger
        //                                 onClick={removeExtraOption}
        //                             />
        //                         </div>
        //                     ) : (
        //                         <></>
        //                     )}
        //                 </Space>
        //             );
        //         } else {
        //             return (
        //                 <Space direction="vertical" style={{ width: '100%', marginTop: '10px' }}>
        //                     {data.options.map((item, index) => {
        //                         return (
        //                             <div style={{ display: 'flex', gap: '5px' }} key={index}>
        //                                 <Input addonBefore="Option" value={item.content} onChange={(e) => handleChangeOption(e, index)} />
        //                                 {index == 0 ?
        //                                     (
        //                                         <Button
        //                                             type="primary"
        //                                             shape="circle"
        //                                             icon={<PlusOutlined />}
        //                                             onClick={addOption}
        //                                         />
        //                                     ) : (
        //                                         <Button
        //                                             type="primary"
        //                                             shape="circle"
        //                                             icon={<MinusOutlined />}
        //                                             danger
        //                                             onClick={() => removeOption(index)}
        //                                         />
        //                                     )
        //                                 }
        //                             </div>
        //                         )
        //                     })}
        //                 </Space>
        //             );
        //         }
        //         break;
        //     default:
        //         break;
        // }
    }

    const addOption = () => {
        setData(state => ({
            ...state,
            options: [...state.options, {
                content: "",
                is_active: true,
            }]
        }));
    }

    const removeOption = (index) => {
        let array = [...data.options]; // make a separate copy of the array
        array.splice(index, 1);
        setData({
            ...data,
            options: array
        });
    }

    return (
        <Modal open={modalQuestion} closeIcon={null} destroyOnClose={true}
            footer={[
                <Button key="back" onClick={handleCancel}>
                    Close
                </Button>,
                <Button key="submit" type="primary" onClick={isUpdate ? handleUpdate : handleCreate}>
                    {isUpdate ? 'Update' : 'Create'}
                </Button>,
            ]}
        >
            <div style={{ textAlign: 'center', marginBottom: '10px', fontSize: '20px' }}>
                {isUpdate
                    ? <p>
                        <span style={{ color: '#92CF69' }}>Edit</span> <span style={{ color: '#5B9BD5' }}>Question</span>
                    </p>
                    : <p>
                        <span style={{ color: '#92CF69' }}>Create</span> <span style={{ color: '#5B9BD5' }}>Question</span>
                    </p>}
            </div>
            <div>
                <Space direction="vertical" style={{ width: '100%', marginTop: '10px' }}>
                    <Input name="content" placeholder="Question Content" value={data.content} onChange={handleChange} />
                    {isUpdate
                        ? <Select
                            placeholder="Question Type"
                            style={{
                                width: '100%',
                            }}
                            onChange={handleChangeSelect}
                            options={questionTypes.map((item) => ({
                                value: item.id,
                                label: item.name
                            }))}
                            value={data.question_type}
                            disabled={isUpdate}
                        />
                        : <Select
                            placeholder="Question Type"
                            style={{
                                width: '100%',
                            }}
                            onChange={handleChangeSelect}
                            options={questionTypes.map((item) => ({
                                value: item.id,
                                label: item.name
                            }))}
                        />}
                    {renderQuestionOption(data.question_type)}
                </Space>
            </div>
        </Modal>
    )
}

export default QuestionModal