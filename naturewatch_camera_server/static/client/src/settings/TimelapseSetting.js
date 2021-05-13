import React from 'react';
import {ToggleButtonGroup, ToggleButton} from 'react-bootstrap';

class TimelapseSetting extends React.Component {



    renderIntervalText(seconds) {

        var it = "";
        
        if (seconds >= 3600) {

            var h = Math.floor(seconds / 3600);
            seconds = seconds % 3600;

            it += String(h) + " hour" + (h > 1 ? "s" : "")
                + (seconds > 0 ? " and " : "");
        }

        if (seconds >= 60) {

            var m = Math.floor(seconds / 60);
            seconds = seconds % 60;

            it += String(m) + " minute" + (m > 1 ? "s" : "")
                + ( seconds > 0 ? " and " : "");
        }

        if (seconds > 0) {
            it += String(seconds) + " second" + (seconds > 1 ? "s" : "");
        }

        return it;
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
                        min="1"
                        max="88"
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
                <ToggleButtonGroup
                  name="timelapse"
                  value={this.props.isActive ? "on" : "off" }
                  onChange={this.props.onActiveChange}
                >
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
