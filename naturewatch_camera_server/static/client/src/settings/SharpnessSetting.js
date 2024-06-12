import React from 'react';
import { ToggleButtonGroup, ToggleButton } from 'react-bootstrap';

class SharpnessSetting extends React.Component {
    constructor(props) {
        super(props);

        this.onSharpnessChange = this.onSharpnessChange.bind(this);
        this.onSharpnessChangeEnd = this.onSharpnessChangeEnd.bind(this);

        this.sharpnessvals = {
            "0": 0,
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "11": 11,
            "12": 12,
            "13": 13,
            "14": 14,
            "15": 15,
            "16": 16
        };
    }

    renderSharpness(sharpnessVal) {
        if (this.props.sharpnessMode === "auto") {
            return "auto";
        }
        else {
            return Object.keys(this.sharpnessvals)[this.getIndexFromSharpnessVal(sharpnessVal)];
        }
    }

    // Inspired from https://www.codevscolor.com/javascript-nearest-number-in-array#method-3-using-sort-
    findClosest = (arr, num) => {
        if (arr == null) {
            return
        }
        return arr.sort((a, b) => Math.abs(b - num) - Math.abs(a - num)).pop();
    }

    getIndexFromSharpnessVal(sharpnessVal) {
        // Get nearest value
        sharpnessVal = this.findClosest(Object.values(this.sharpnessvals), sharpnessVal)

        for (var i = 0; i < Object.keys(this.sharpnessvals).length; i++) {
            if (Object.values(this.sharpnessvals)[i] === sharpnessVal) {
                return i;
            }
        }
        return 0;
    }

    getSharpnessValFromIndex(index) {
        return Object.values(this.sharpnessvals)[index];
    }

    onSharpnessChange(event) {
        this.props.onSharpnessChange(this.getSharpnessValFromIndex(event.target.value));
    }

    onSharpnessChangeEnd(event) {
        this.props.onSharpnessChangeEnd(this.getSharpnessValFromIndex(event.target.value));
    }

    renderSharpnessSettings() {
        if (this.props.sharpnessMode !== "auto") {
            return (
                <div>
                    <label htmlFor="sharpness-val" className="sharpness-val-label">
                        Sharpness: <span>{this.renderSharpness(this.props.sharpnessVal)}</span>
                    </label>
                    <br />
                    <input
                        type="range"
                        id="sharpness-val"
                        min="0"
                        max={Object.keys(this.sharpnessvals).length - 1}
                        step="1"
                        value={this.getIndexFromSharpnessVal(this.props.sharpnessVal)}
                        onChange={this.onSharpnessChange}
                        onMouseUp={this.onSharpnessChangeEnd}
                        onTouchEnd={this.onSharpnessChangeEnd}
                    />
                </div>
            );
        }
    }

    render() {
        return (
            <div>
                <ToggleButtonGroup name="sharpness" value={this.props.sharpnessMode} onChange={this.props.onSharpnessModeChange}>
                    <ToggleButton type="radio" value="auto">Auto</ToggleButton>
                    <ToggleButton type="radio" value="manual">Manual</ToggleButton>
                </ToggleButtonGroup>
                <br />
                {this.renderSharpnessSettings()}
            </div>
        );
    }
}

export default SharpnessSetting;