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
        this.onTimelapseActiveChange = this.onTimelapseActiveChange.bind(this);

        this.state = {
            feedStatus: "active",
            sessionStatus: {
                mode: "inactive",
                time_started: 0
            },
            isSettingsOpen: false,
            isTimelapseActive: false,
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
        //let currentTime = this.formatTime(new Date());
        let currentTime = Date.now() / 1000;
        axios.post('/api/time/' + currentTime)
            .then((res) => {
                const status = res.data;
                console.log("INFO: Sent time " + currentTime + " to camera.");
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

    formatTime(d) {
        let year = d.getFullYear().toString();
        let month = "";
        if (d.getMonth()+1 < 10) {
            month = "0" + (d.getMonth()+1).toString();
        } else {
            month += (d.getMonth()+1).toString();
        }
        let date = "";
        if (d.getDate() < 10) {
            date = "0" + d.getDate().toString();
        } else {
            date = d.getDate().toString();
        }
        let hours = "";
        if (d.getHours() < 10) {
            hours = "0" + d.getHours().toString();
        } else {
            hours = d.getHours().toString();
        }
        let minutes = "";
        if (d.getMinutes() < 10) {
            minutes = "0" + d.getMinutes().toString();
        } else {
            minutes = d.getMinutes().toString();
        }
        let seconds = "";
        if (d.getSeconds() < 10) {
            seconds = "0" + d.getSeconds().toString();
        } else {
            seconds = d.getSeconds().toString();
        }

        return year + "-" + month + "-" + date + " " + hours + ":" + minutes + ":" + seconds;
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

    onTimelapseActiveChange(value) {
        this.setState({isTimelapseActive: value === "on" ? true : false},
            () => {
                console.log("Timelapse: " + this.state.isTimelapseActive);
            });
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
                                        type={this.state.isTimelapseActive ? "timelapse" : "photo"}
                                        onButtonClick={this.onSessionButtonClick}
                                        sessionStatus={this.state.sessionStatus.mode}
                                    />
                                </Col>
                            </Row>}
                            <Settings
                                isOpen={this.state.isSettingsOpen}
                                onOpen={this.onSettingsOpen}
                                onClose={this.onSettingsClose}
                                onTimelapseActiveChange={this.onTimelapseActiveChange}
                                isTimelapseActive={this.state.isTimelapseActive}
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
