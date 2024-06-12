import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class LEDSetting extends React.Component {
    render() {
        return (
            <ToggleButtonGroup name="LED" value={this.props.value} onChange={this.props.onValueChange}>
                <ToggleButton type="radio" value="off">Off</ToggleButton>
                <ToggleButton type="radio" value="on">On</ToggleButton>
            </ToggleButtonGroup>
        );
    }
}

export default LEDSetting;