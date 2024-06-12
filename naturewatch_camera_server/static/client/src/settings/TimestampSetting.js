import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class TimestampSetting extends React.Component {
    render() {
        return (
            <ToggleButtonGroup name="timestamp" value={this.props.value} onChange={this.props.onValueChange}>
                <ToggleButton type="radio" value="off">Disabled</ToggleButton>
                <ToggleButton type="radio" value="on">Enabled</ToggleButton>
            </ToggleButtonGroup>
        );
    }
}

export default TimestampSetting;