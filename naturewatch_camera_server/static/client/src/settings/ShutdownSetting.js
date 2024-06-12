import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class ShutdownSetting extends React.Component {
    render() {
        return (
            <ToggleButtonGroup name="Shutdown" value={this.props.value} onChange={this.props.onValueChange}>
                <ToggleButton type="radio" value="0">Shutdown</ToggleButton>
                <ToggleButton type="radio" value="1">Restart</ToggleButton>
            </ToggleButtonGroup>
        );
    }
}

export default ShutdownSetting;