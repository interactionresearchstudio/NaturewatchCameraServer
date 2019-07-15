import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class ExposureSetting extends React.Component {
    render() {
        return (
            <div>
                <ToggleButtonGroup name="exposure" value={this.props.mode} onChange={this.props.onModeChange}>
                    <ToggleButton type="radio" value="auto">Auto</ToggleButton>
                    <ToggleButton type="radio" value="manual">Manual</ToggleButton>
                </ToggleButtonGroup>
                <label htmlFor="shutter-speed">Fixed Shutter Speed: </label>
                <input
                    type="range"
                    id="shutter-speed"
                    min="0"
                    max="21"
                    step="1"
                    value={this.props.speed}
                    onChange={this.props.onShutterChange}
                />
            </div>
        );
    }
}

export default ExposureSetting;