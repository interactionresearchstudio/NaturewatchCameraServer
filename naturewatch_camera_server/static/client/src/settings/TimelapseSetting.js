import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class TimelapseSetting extends React.Component {

    onIntervalChange(event) {
        this.props.onIntervalChange(event.target.value);
    }

    onIntervalChangeEnd(event) {
        this.props.onIntervalEnd(event.target.value);
    }

    renderIntervalText(seconds) {
        if (seconds > 59) {
            return Math.round((seconds / 60)) + " minutes";
        } else {
            return seconds + " seconds";
        }
    }

    calculateSliderStep(seconds) {
        if (seconds >= 3600) return 600;
        if (seconds >= 600) return 300;
        if (seconds >= 120) return 60;
        return 10;
    }

    renderDetailedSettings() {
        if (this.props.isActive) {
            return (
                <div>
                    <label htmlFor="interval" className="interval-label">
                        Interval: <span>{this.renderIntervalText(this.props.interval)}</span>
                    </label>
                    <br/>
                    <input
                        type="range"
                        id="interval"
                        min="0"
                        max="100"
                        defaultValue="1"
                        step="1"
                        value={this.props.intervalPos}
                        onChange={this.props.onChange}
                        onMouseUp={this.props.onChangeEnd}
                        onTouchEnd={this.props.onChangeEnd}
                    />
                </div>
            );
        }
    }

    render() {
        return (
            <div>
                <ToggleButtonGroup name="exposure" value={this.props.isActive ? "on" : "off" } onChange={this.props.onActiveChange}>
                    <ToggleButton type="radio" value="off">Off</ToggleButton>
                    <ToggleButton type="radio" value="on">On</ToggleButton>
                </ToggleButtonGroup>
                <br/>
                {this.renderDetailedSettings()}
            </div>
        );
    }
}

export default TimelapseSetting;