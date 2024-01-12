'use client'
import React, { useEffect } from 'react';
import Layout, { Content, Header } from 'antd/es/layout/layout';
import Sider from 'antd/es/layout/Sider';
import { Button, Menu } from 'antd';
import {
    UserOutlined,
    QuestionCircleOutlined,
    TeamOutlined,
    SnippetsOutlined
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import { clearToken, getToken } from '@/utils/token';
import { redirect } from 'next/navigation';

function getItem(label, key, icon, children) {
    return {
        key,
        icon,
        children,
        label,
    };
}
const items = [
    getItem('Survey', '/dashboard/survey', <SnippetsOutlined />),
    getItem('Question', '/dashboard/question', <QuestionCircleOutlined />),
    getItem('Group', '/dashboard/group', <TeamOutlined />),
    getItem('Participant', '/dashboard/participant', <UserOutlined />),
];

export default function BaseLayout({ children }) {
    const token = getToken();

    if (token == "") {
        redirect("/");
    }

    const router = useRouter()

    const logout = () => {
        clearToken();
        router.push('/login')
    }

    return (
        <Layout
            style={{
                minHeight: '100vh',
            }}
        >
            <Sider style={{ background: 'white' }} width={250}>
                <img src="/images/logo.png" alt="logo" style={{ padding: '20px' }} />
                <Menu defaultSelectedKeys={['/dashboard/survey']} mode="inline" items={items} onClick={(e) => router.push(e.key)} />

                <Button style={{ display: 'flex', margin: 'auto' }} onClick={logout}>Logout</Button>
            </Sider>
            <Layout>
                <Content
                    style={{
                        margin: '20px 16px',
                        background: 'white'
                    }}
                >
                    <div
                        style={{
                            padding: 24,
                            minHeight: 360,
                        }}
                    >
                        {children}
                    </div>
                </Content>
            </Layout>
        </Layout >
    )
}
