import React from 'react';
import {Container, Row, Col} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import IdleTimer from 'react-idle-timer';
import axios from 'axios';
import Header from './Header'
import CameraFeed from './CameraFeed'
import Settings from '../settings/Settings';
import SessionButton from './SessionButton';

class Index extends React.Component {
    constructor(props) {
        super(props);

        this.idleTimer = null;

        this.onSessionButtonClick = this.onSessionButtonClick.bind(this);
        this.onIdle = this.onIdle.bind(this);
        this.handleFeedRefresh = this.handleFeedRefresh.bind(this);
        this.onSettingsOpen = this.onSettingsOpen.bind(this);
        this.onSettingsClose = this.onSettingsClose.bind(this);

        this.state = {
            feedStatus: "active",
            sessionStatus: {
                mode: "inactive",
                time_started: 0
            },
            isSettingsOpen: false
        };
    }

    componentDidMount() {
        // Get session object form camera
        axios.get('/api/session')
            .then((res) => {
                const status = res.data;
                this.setState({sessionStatus: status});
                console.log("INFO: status received.");
                console.log(this.state.sessionStatus);
            });
        // Send time to camera.
        let currentTime = Math.round((new Date()).getTime() / 1000);
        axios.get('/api/time/' + currentTime)
            .then((res) => {
                const status = res.data;
                console.log("INFO: Sent time to camera.");
                console.log(status);
            });
    }

    captureStatus() {
        if (this.state.sessionStatus.mode === "inactive") {
            return (
                <p className="feed-status">Capture is <u>off</u></p>
            );
        } else {
            return (
                <p className="feed-status">Capture is <u>on</u></p>
            );
        }
    }

    getSessionButtonText(type) {
        // Deal with terminology...
        if (type === "photo") type = "image";
        let session = this.state.sessionStatus.mode;
        if (session === "photo") type = "image";

        if (session === type) {
            return "Stop " + type + " Capture";
        }
        else {
            return "Start " + type + " Capture";
        }
    }

    onSessionButtonClick(type) {
        if (this.state.sessionStatus.mode === "inactive") {
            axios.post('/api/session/start/' + type)
                .then((res) => {
                    this.setState({
                        sessionStatus: res.data
                    }, () => {
                        console.log(this.state.sessionStatus);
                    });
                }).catch(() => {
                    console.log("ERROR: POST request failed whilst opening session.");
                });
        } else {
            axios.post('/api/session/stop')
                .then((res) => {
                    this.setState({
                        sessionStatus: res.data
                    }, () => {
                        console.log(this.state.sessionStatus);
                    });
                }).catch(() => {
                    console.log("ERROR: POST request failed whilst closing session.");
                });
        }
    }

    onIdle() {
        console.log("INFO: Feed status timeout.");
        this.setState({
            feedStatus: "inactive"
        });
    }

    handleFeedRefresh() {
        console.log("INFO: Feed refreshed.");
        this.setState({
            feedStatus: "active"
        });
    }

    onSettingsOpen() {
        this.setState({isSettingsOpen: true});
    }

    onSettingsClose() {
        this.setState({isSettingsOpen: false});
    }

    render() {
        return(
            <div className="index">
                <Container>
                    <Row>
                        <Col>
                            <Header/>
                        </Col>
                    </Row>
                    <Row>
                        <Col sm={8}>
                            <CameraFeed
                                status={this.state.feedStatus}
                                onClick={this.handleFeedRefresh}
                            />
                            {this.captureStatus()}
                        </Col>
                        <Col sm={4}>
                            {!this.state.isSettingsOpen && <Row>
                                <Col xs={6}>
                                    <SessionButton
                                        type={"video"}
                                        onButtonClick={this.onSessionButtonClick}
                                        sessionStatus={this.state.sessionStatus.mode}
                                    />
                                </Col>
                                <Col xs={6}>
                                    <SessionButton
                                        type={"photo"}
                                        onButtonClick={this.onSessionButtonClick}
                                        sessionStatus={this.state.sessionStatus.mode}
                                    />
                                </Col>
                            </Row>}
                            <Settings
                                isOpen={this.state.isSettingsOpen}
                                onOpen={this.onSettingsOpen}
                                onClose={this.onSettingsClose}
                            />
                            {!this.state.isSettingsOpen && <Link to="/gallery" className="btn btn-secondary">Gallery</Link>}
                        </Col>
                    </Row>
                </Container>
                <IdleTimer
                    ref={ref => { this.idleTimer = ref }}
                    element={document}
                    onIdle={this.onIdle}
		            debounce={250}
                    timeout={1000 * 60}
                />
            </div>
        );
    }
}

export default Index;
