import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class ExposureSetting extends React.Component {
    constructor(props) {
        super(props);

        this.cameraShutterSpeeds = {
            "1/30": 33333,
            "1/40": 25000,
            "1/50": 20000,
            "1/60": 16666,
            "1/80": 12500,
            "1/100": 10000,
            "1/125": 8000,
            "1/160": 6250,
            "1/200": 5000,
            "1/250": 4000,
            "1/320": 3125,
            "1/400": 2500,
            "1/500": 2000,
            "1/640": 1563,
            "1/800": 1250,
            "1/1000": 1000,
            "1/1250": 800,
            "1/1600": 625,
            "1/2000": 500,
            "1/2500": 400,
            "1/3200": 313,
            "1/4000": 250
        };
    }

    renderShutterSpeedFraction(index) {
        if (this.props.mode === "auto") {
            return "auto";
        }
        else {
            return Object.keys(this.cameraShutterSpeeds)[index];
        }
    }

    getIndexFromShutterSpeed(shutterSpeed) {
        for (var i=0; i < Object.keys(this.cameraShutterSpeeds).length; i++) {
            if (Object.values(this.cameraShutterSpeeds)[i] == shutterSpeed) {
                return i;
            }
        }
        return 0;
    }

    getShutterSpeedFromIndex(index) {
        return Object.values(this.cameraShutterSpeeds)[index];
    }

    onShutterChange(e) {
        this.props.onShutterChange(this.getShutterSpeedFromIndex(e.target.value));
    }

    renderDetailedSettings() {
        if (this.props.mode !== "auto") {
            return (
                <div>
                    <label htmlFor="shutter-speed">
                        Fixed Shutter Speed: <span>{this.renderShutterSpeedFraction(this.props.shutterSpeed)}</span>
                    </label>
                    <br/>
                    <input
                        type="range"
                        id="shutter-speed"
                        min="0"
                        max={Object.keys(this.cameraShutterSpeeds).length}
                        step="1"
                        value={this.getIndexFromShutterSpeed(this.props.shutterSpeed)}
                        onChange={this.props.onShutterChange}
                    />
                </div>
            );
        }
    }

    render() {
        return (
            <div>
                <ToggleButtonGroup name="exposure" value={this.props.mode} onChange={this.props.onModeChange}>
                    <ToggleButton type="radio" value="auto">Auto</ToggleButton>
                    <ToggleButton type="radio" value="off">Manual</ToggleButton>
                </ToggleButtonGroup>
                <br/>
                {this.renderDetailedSettings()}
            </div>
        );
    }
}

export default ExposureSetting;