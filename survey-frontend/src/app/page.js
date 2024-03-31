'use client'
import React from 'react';
import Layout, { Content } from 'antd/es/layout/layout';
import Sider from 'antd/es/layout/Sider';
import { Menu } from 'antd';
import {
  DesktopOutlined,
  FileOutlined,
  PieChartOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

function getItem(label, key, icon, children) {
  return {
    key,
    icon,
    children,
    label,
  };
}
const items = [
  getItem('Survey', '/survey', <PieChartOutlined />),
  getItem('Question', '/question', <DesktopOutlined />),
  getItem('Group', '/group', <TeamOutlined />),
  getItem('Participant', '/participant', <FileOutlined />),
  getItem('Logout', '/logout', <FileOutlined />),
];

export default function BaseLayout({ children }) {
  const router = useRouter()

  return (
    <Layout
      style={{
        minHeight: '100vh',
      }}
    >
      <Sider style={{ background: 'white' }}>
        <Image src="/images/logo.png" alt="logo" style={{ marginBottom: '20px' }} width={300}
                                height={200}
                                sizes="100vw" />
        <Menu defaultSelectedKeys={['/survey']} mode="inline" items={items} onClick={(e)=>router.push(e.key)}/>
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
    </Layout>
  )
}
