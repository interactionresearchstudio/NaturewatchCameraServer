import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class ResolutionSetting extends React.Component {
    render() {
        return (
            <ToggleButtonGroup name="resolution" value={this.props.value} onChange={this.props.onValueChange}>
                <ToggleButton type="radio" value="1640x1232">1640x1232</ToggleButton>
                <ToggleButton type="radio" value="1920x1080">1920x1080</ToggleButton>
            </ToggleButtonGroup>
        );
    }
}

export default ResolutionSetting;