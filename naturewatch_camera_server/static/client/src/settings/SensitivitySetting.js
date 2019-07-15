import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class SensitivitySetting extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        this.props.onValueChange(e);
    }

    render() {
        return (
            <ToggleButtonGroup type="checkbox" value={this.props.value} onChange={this.props.onValueChange}>
                <ToggleButton value={{max: 200, min: 150}}>Less</ToggleButton>
                <ToggleButton value={{max: 200, min: 100}}>Default</ToggleButton>
                <ToggleButton value={{max: 200, min: 50}}>More</ToggleButton>
            </ToggleButtonGroup>
        );
    }
}

export default SensitivitySetting;