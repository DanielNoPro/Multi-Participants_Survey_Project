import Layout, { Content, Footer, Header } from 'antd/es/layout/layout'
import React from 'react'
import moment from 'moment';
import Image from 'next/image';


export default function Page() {
    const renderSurvey = () => {
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
                            <p style={{ color: '#1BB12A', fontSize: '18px', fontWeight: '500' }}>Your access to this survey has been revoked</p>
                            <Image src="/images/warning.png" alt="logo" style={{ padding: '20px', margin: "auto" }} width={200}
                                height={200}
                                sizes="100vw" />
                        </div>
                    </div>
                </Content>
            </Layout>
        )
    }

    return (
        <div>
            {renderSurvey()}
        </div>
    )
}
