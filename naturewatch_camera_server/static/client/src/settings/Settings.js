import React from 'react';
import axios from 'axios';
import {Button, Collapse, Accordion, Card} from 'react-bootstrap';
import SensitivitySetting from './SensitivitySetting';
import ExposureSetting from './ExposureSetting';
import TimelapseSetting from './TimelapseSetting';
import PropTypes from "prop-types";

class Settings extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.onSensitivityChange = this.onSensitivityChange.bind(this);
        this.onImageOrientationChange = this.onImageOrientationChange.bind(this);
        this.onShutterChange = this.onShutterChange.bind(this);
        this.onShutterChangeEnd = this.onShutterChangeEnd.bind(this);
        this.onModeChange = this.onModeChange.bind(this);
        this.onTimelapseActiveChange = this.onTimelapseActiveChange.bind(this);
        this.onIntervalChange = this.onIntervalChange.bind(this);
        this.onIntervalChangeEnd = this.onIntervalChangeEnd.bind(this);
        

        this.state = {
            isOpen: false,
            settings: {
                rotation: null,
                exposure: {
                    mode: "",
                    iso: "",
                    shutter_speed: ""
                },
                sensitivity: "",
                timelapse : {
                    active: false,
                    interval: 0
                }
            }
        };

        this.timeslapse = [
            [24,10],
            [24,30],
            [24,60],
            [16,300],
        ];
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
                this.props.onTimelapseActiveChange(
                    this.state.settings.timelapse.active ? "on" : "off",
                );
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
            console.log("INFO: Changed exposure mode.");
            this.postSettings();
        });
    }

    onTimelapseActiveChange(value) {
        let currentSettings = this.state.settings;
        currentSettings.timelapse.active = (value === "on" ? true : false);
        this.props.onTimelapseActiveChange(value)
        console.log("timelapse_active: " + String(currentSettings.timelapse.active));
        this.setState({
            settings: currentSettings
        }, () => {
            console.log("INFO: Changed timelapse_active.");
            this.postSettings();
        });
    }

    onIntervalChange(event) {
        let currentSettings = this.state.settings;
        currentSettings.timelapse.interval = this.intervalPosToValue(event.target.valueAsNumber);
        console.log("Interval: " + currentSettings.timelapse.interval
                    + "; slider.value = " + event.target.valueAsNumber);
        this.setState({
            settings: currentSettings
        });
    }

    onIntervalChangeEnd(event) {
        let currentSettings = this.state.settings;
        currentSettings.timelapse.duration = this.intervalPosToValue(event.target.valueAsNumber);
        this.setState({
            settings: currentSettings
        }, () => {
            this.postSettings();
        });
    }

    intervalValueToPos(val) {

        var position = 0;
        for (var i=0; i<this.timeslapse.length; i++) {

            let lookup = this.timeslapse[i];
            if (val <= lookup[0] * lookup[1]) {
                position += Math.floor(val / lookup[1]);
                return position
            }
            val -= lookup[0] * lookup[1];
            position += lookup[0];
        }

        return position;
    }

    intervalPosToValue(position) {

        var res = 0;
        for (var i=0; i<this.timeslapse.length; i++) {

            let lookup = this.timeslapse[i];
            if (position <= lookup[0]) {
                res += position * lookup[1];
                return res;
            }
            res += lookup[0] * lookup[1];
            position -= lookup[0];
        }

        return res;
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
                            <Accordion.Toggle as={Card.Header} eventKey={1}>
                                Sensitivity
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={1}>
                                <Card.Body>
                                    <SensitivitySetting
                                        onValueChange={this.onSensitivityChange}
                                        value={this.state.settings.sensitivity}
                                    />
                                </Card.Body>
                            </Accordion.Collapse>
                        </Card>
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={2}>
                                Image Orientation
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={2}>
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
                            <Accordion.Toggle as={Card.Header} eventKey={3}>
                                Exposure
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={3}>
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
                        <Card>
                            <Accordion.Toggle as={Card.Header} eventKey={4}>
                                Timelapse Mode
                            </Accordion.Toggle>
                            <Accordion.Collapse eventKey={4}>
                                <Card.Body>
                                    <TimelapseSetting
                                        isActive={this.props.isTimelapseActive}
                                        onChange={this.onIntervalChange}
                                        onChangeEnd={this.onIntervalChangeEnd}
                                        onActiveChange={this.onTimelapseActiveChange}
                                        intervalPos={this.intervalValueToPos(this.state.settings.timelapse.interval)}
                                        interval={this.state.settings.timelapse.interval}
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
