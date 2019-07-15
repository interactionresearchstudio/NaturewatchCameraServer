import React from 'react';
import axios from 'axios';
import {Button, Collapse, Accordion, Card} from 'react-bootstrap';
import SensitivitySetting from '../settings/SensitivitySetting';

class Settings extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.onSensitivityChange = this.onSensitivityChange.bind(this);

        this.state = {
            isOpen: false,
            settings: {
            }
        };
    }

    componentDidMount() {
        this.getSettings();
    }

    getSettings() {
        axios.get('/api/settings')
            .then((res) => {
                const settings = res.data;
                this.setState({settings});
                console.log("INFO: settings updated. ");
                console.log(this.state.settings);
            });
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

    onSensitivityChange(value) {
        console.log("INFO: Received sensitivity value");
        console.log(value);
        /*
        const sensitivity = value;
        this.setState({
            settings: {sensitivity}
        });
        console.log("INFO: Changed sensitivity.");
        console.log(this.state.settings.sensitivity);

         */
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
                                    <SensitivitySetting onValueChange={this.onSensitivityChange} value={this.state.settings.sensitivity}/>
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