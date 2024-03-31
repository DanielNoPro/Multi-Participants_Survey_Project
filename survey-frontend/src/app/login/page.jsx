'use client';
import React from 'react';
import { Button, Checkbox, Col, Form, Input, Row } from 'antd';
import { authService } from '@/services/authService';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

const LoginPage = () => {
    const router = useRouter()

    const onFinish = async (values) => {
        const res = await authService.login(values);
        if (res) {
            router.push("/dashboard/survey")
        }
    };
    const onFinishFailed = (errorInfo) => {
        console.log('Failed:', errorInfo);
    };

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            width: '100vw',
            height: '100vh',
            backgroundImage: `url("/images/login_bg.png")`,
            backgroundSize: 'cover',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center center',
            padding: '50px'
        }}>
            <div style={{
                backgroundColor: 'rgb(217, 217, 217, 0.5)',
                height: '100%',
                width: '100%',
                borderRadius: '10px'
            }}>
                <Row style={{
                    height: '100%',
                    width: '100%',
                }}>
                    <Col span={12} style={{ padding: '30px' }}>
                        <p style={{
                            color: 'white',
                            fontSize: '20px'
                        }}>AUT- Project Team 4</p>
                        <p style={{
                            fontWeight: '700',
                            color: 'white',
                            fontSize: '32px'
                        }}>Multi-Participants Survey</p>
                        <div style={{
                            position: 'absolute',
                            top: '35%',
                            transform: 'translate(0, -50 %)',
                            paddingLeft: '30px',
                            color: '#00FFF0',
                            fontSize: '50px',
                            fontWeight: '700',
                            fontFamily: 'K2D'
                        }}>
                            <p>
                                DO SURVEY
                            </p>
                            <p>
                                EASIER
                            </p>
                        </div>
                        <div style={{
                            position: 'absolute',
                            top: '75%',
                            left: '50%',
                            transform: 'translate(-40%)'
                        }}>
                            <p style={{
                                color: 'white',
                                fontSize: '15px',
                                paddingLeft: '40px'
                            }}>Associate with</p>
                            <Image src="/images/logo.png" alt="logo" style={{ width: '70%' }} width={300}
                                height={200}
                                sizes="100vw" />
                        </div>
                    </Col>
                    <Col span={12} style={{
                        padding: '40px'
                    }}>
                        <div style={{ textAlign: 'center', color: 'white' }}>
                            <p style={{
                                fontSize: '50px',
                                fontWeight: '500'
                            }}>Hello!</p>
                            <p style={{
                                fontSize: '20px',
                            }}>Welcome to our survey</p>
                        </div>
                        <Form
                            name="basic"
                            style={{
                                width: '500px',
                                position: 'absolute',
                                top: '40%',
                                left: '15%',
                            }}
                            onFinish={onFinish}
                            onFinishFailed={onFinishFailed}
                            autoComplete="off"
                        >
                            <Form.Item
                                name="email"
                                rules={[
                                    {
                                        required: true,
                                        message: 'Please input your email!',
                                    },
                                ]}
                                style={{ marginBottom: '50px' }}
                            >
                                <Input placeholder="Email" size="large" />
                            </Form.Item>

                            <Form.Item
                                name="password"
                                rules={[
                                    {
                                        required: true,
                                        message: 'Please input your password!',
                                    },
                                ]}
                            >
                                <Input.Password placeholder="Password" size="large" />
                            </Form.Item>

                            <Form.Item
                                style={{ textAlign: 'center' }}
                            >
                                <Button type="primary" htmlType="submit">
                                    Log in
                                </Button>
                            </Form.Item>
                        </Form>
                    </Col>
                </Row>
            </div>
        </div>
    )
};
export default LoginPage;