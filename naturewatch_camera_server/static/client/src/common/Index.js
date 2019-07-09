import React from 'react';
import {Container, Row, Col} from 'react-bootstrap';
import Header from './Header'
import CameraFeed from './CameraFeed'
import Settings from './Settings';

class Index extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            feedStatus: "active"
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
                            <Settings/>
                        </Col>
                    </Row>
                </Container>
            </div>
        );
    }
}

export default Index;
