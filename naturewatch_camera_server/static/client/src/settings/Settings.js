import React from 'react';
import axios from 'axios';
import {Button, Collapse, Accordion, Card} from 'react-bootstrap';
import SensitivitySetting from './SensitivitySetting';
import ExposureSetting from './ExposureSetting';
import PropTypes from "prop-types";

class Settings extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.onSensitivityChange = this.onSensitivityChange.bind(this);
        this.onImageOrientationChange = this.onImageOrientationChange.bind(this);
        this.onShutterChange = this.onShutterChange.bind(this);
        this.onShutterChangeEnd = this.onShutterChangeEnd.bind(this);
        this.onModeChange = this.onModeChange.bind(this);

        this.state = {
            isOpen: false,
            settings: {
                rotation: null,
                exposure: {
                    mode: "",
                    iso: "",
                    shutter_speed: ""
                },
                sensitivity: ""
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
                this.setState({settings: settings});
                console.log("INFO: settings received.");
                console.log(this.state.settings);
            });
    }

    postSettings() {
        console.log(this.state.settings);
        axios.post('api/settings', this.state.settings)
            .then((res) => {
                console.log("INFO: settings sent.");
                const settings = res.data;
                this.setState({settings: settings}, () => {
                    console.log("INFO: Updated settings");
                    console.log(this.state.settings);
                });
            });
    }

    renderBackButton() {
        if (this.props.isOpen) {
            return (
                <Button
                    variant="secondary"
                    onClick={this.props.onClose}
                    aria-controls="collapse-settings"
                    aria-expanded="false"
                    className="short"
                >
                    Back
                </Button>
            )
        }
        else return null;
    }

    onSensitivityChange(value) {
        console.log("INFO: Received sensitivity value");
        console.log(value);
        let currentSettings = this.state.settings;

        console.log("Current settings: ");
        console.log(currentSettings);

        currentSettings.sensitivity = value;

        console.log("Changed settings: ");
        console.log(currentSettings);
        this.setState({
            settings: currentSettings
        }, () => {
            console.log("INFO: Changed sensitivity.");
            console.log(this.state.settings);
            this.postSettings();
        });
    }

    onImageOrientationChange() {
        let currentSettings = this.state.settings;
        currentSettings.rotation = !currentSettings.rotation;
        this.setState({
            settings: currentSettings
        }, () => {
            console.log("INFO: Changed orientation.");
            this.postSettings();
        });
    }

    onShutterChange(val) {
        let currentSettings = this.state.settings;
        currentSettings.exposure.shutter_speed = val;
        this.setState({
            settings: currentSettings
        });
    }

    onShutterChangeEnd(val) {
        let currentSettings = this.state.settings;
        currentSettings.exposure.shutter_speed = val;
        this.setState({
            settings: currentSettings
        }, () => {
            console.log("INFO: Changed shutter speed.");
            this.postSettings();
        });
    }

    onModeChange(value) {
        let currentSettings = this.state.settings;
        currentSettings.exposure.mode = value;
        this.setState({
            settings: currentSettings
        }, () => {
            console.log("INFO: Changed exposure mode");
            this.postSettings();
        });
    }

    render() {
        return (
            <div className="settings">
                <Button
                    variant="secondary"
                    onClick={this.props.onOpen}
                    aria-controls="collapse-settings"
                    aria-expanded={this.props.isOpen}
                    className="settings-button"
                >
                    Settings
                </Button>
                <Collapse in={this.props.isOpen}>
                    <Accordion>
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={0}>
                                Sensitivity
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={0}>
                                <Card.Body>
                                    <SensitivitySetting
                                        onValueChange={this.onSensitivityChange}
                                        value={this.state.settings.sensitivity}
                                    />
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={1}>
                                Image Orientation
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={1}>
                                <Card.Body>
                                    <Button
                                        variant="primary"
                                        onClick={this.onImageOrientationChange}
                                    >
                                        Flip 180
                                    </Button>
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={2}>
                                Exposure
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={2}>
                                <Card.Body>
                                    <ExposureSetting
                                        mode={this.state.settings.exposure.mode}
                                        shutterSpeed={this.state.settings.exposure.shutter_speed}
                                        onShutterChange={this.onShutterChange}
                                        onShutterChangeEnd={this.onShutterChangeEnd}
                                        onModeChange={this.onModeChange}
                                    />
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

Settings.propTypes = {
    onOpen: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired,
    isOpen: PropTypes.bool.isRequired
};

export default Settings;