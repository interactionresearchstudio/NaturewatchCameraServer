import React from 'react';
import {Container, Row, Col} from 'react-bootstrap';
import Header from './Header'
import CameraFeed from './CameraFeed'
import Settings from '../settings/Settings';
import SessionButton from './SessionButton';

class Index extends React.Component {
    constructor(props) {
        super(props);

        this.onVideoSessionClick = this.onVideoSessionClick.bind(this);
        this.onPhotoSessionClick = this.onPhotoSessionClick.bind(this);

        this.state = {
            feedStatus: "active",
            sessionStatus: "inactive"
        };
    }
    componentDidMount() {
        setTimeout(() => {
            console.log("INFO: Feed status timeout.");
            this.setState({
                feedStatus: "inactive"
            });
        }, 60000);
    }

    captureStatus() {
        if (this.state.feedStatus === "inactive") {
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
        let session = this.state.sessionStatus;
        if (session === "photo") type = "image";

        if (session === type) {
            return "Stop " + type + " Capture";
        }
        else {
            return "Start " + type + " Capture";
        }
    }

    onVideoSessionClick() {

    }

    onPhotoSessionClick() {
        if (this.state.sessionStatus === "inactive") {
            this.setState({
                sessionStatus: "photo"
            })
        }
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
                            <CameraFeed status={this.state.feedStatus}/>
                            {this.captureStatus()}
                        </Col>
                        <Col sm={4}>
                            <SessionButton
                                type={"video"}
                                onButtonClick={this.onSessionButtonClick}
                                sessionStatus={this.state.sessionStatus}
                            />
                            <SessionButton
                                type={"photo"}
                                onButtonClick={this.onSessionButtonClick}
                                sessionStatus={this.state.sessionStatus}
                            />
                            <Settings/>
                        </Col>
                    </Row>
                </Container>
            </div>
        );
    }
}

export default Index;
