import React from 'react';
import {Button, Collapse, Accordion, Card} from 'react-bootstrap';

class Settings extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.state = {
            isOpen: false
        };
    }

    renderBackButton() {
        if (this.state.isOpen) {
            return (
                <Button
                    variant="secondary"
                    onClick={() => this.setState({isOpen: false})}
                    aria-controls="collapse-settings"
                    aria-expanded="false"
                >
                    Back
                </Button>
            )
        }
    }

    render() {
        return (
            <div className="settings">
                <Button
                    variant="secondary"
                    onClick={() => this.setState({isOpen: !this.state.isOpen})}
                    aria-controls="collapse-settings"
                    aria-expanded="true"
                >
                    Settings
                </Button>
                <Collapse in={this.state.isOpen}>
                    <Accordion>
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={0}>
                                Sensitivity
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={0}>
                                <Card.Body>
                                    Sensitivity settings...
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={1}>
                                Image Orientation
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={1}>
                                <Card.Body>
                                    Image Orientation settings...
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={2}>
                                Exposure
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={2}>
                                <Card.Body>
                                    Exposure settings...
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                    </Accordion>
                </Collapse>
                {this.renderBackButton()}
            </div>
        );
    }
}

export default Settings;