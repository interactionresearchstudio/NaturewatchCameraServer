import React from 'react';

class SensitivitySetting extends React.Component {
    constructor(props) {
        super(props);

        this.onSensitivityChange = this.onSensitivityChange.bind(this);
        this.onSensitivityChangeEnd = this.onSensitivityChangeEnd.bind(this);

        this.sensitivityvals = {
            "1": 10,
            "2": 9,
            "3": 8,
            "4": 7,
            "5": 6,
            "6": 5,
            "7": 4,
            "8": 3,
            "9": 2,
            "10": 1
        };
    }

    renderSensitivity(sensitivityVal) {
        return Object.keys(this.sensitivityvals)[this.getIndexFromSensitivityVal(sensitivityVal)];
    }

    // Inspired from https://www.codevscolor.com/javascript-nearest-number-in-array#method-3-using-sort-
    findClosest = (arr, num) => {
        if (arr == null) {
            return
        }
        return arr.sort((a, b) => Math.abs(b - num) - Math.abs(a - num)).pop();
    }

    getIndexFromSensitivityVal(sensitivityVal) {
        // Get nearest value
        sensitivityVal = this.findClosest(Object.values(this.sensitivityvals), sensitivityVal)

        for (var i = 0; i < Object.keys(this.sensitivityvals).length; i++) {
            if (Object.values(this.sensitivityvals)[i] === sensitivityVal) {
                return i;
            }
        }
        return 0;
    }

    getSensitivityValFromIndex(index) {
        return Object.values(this.sensitivityvals)[index];
    }

    onSensitivityChange(event) {
        this.props.onSensitivityChange(this.getSensitivityValFromIndex(event.target.value));
    }

    onSensitivityChangeEnd(event) {
        this.props.onSensitivityChangeEnd(this.getSensitivityValFromIndex(event.target.value));
    }

    renderSensitivitySettings() {
        return (
            <div>
                <label htmlFor="sensitivity-val" className="sensitivity-val-label">
                    Sensitivity: <span>{this.renderSensitivity(this.props.sensitivityVal)}</span>
                </label>
                <br />
                <input
                    type="range"
                    id="sensitivity-val"
                    min="0"
                    max={Object.keys(this.sensitivityvals).length - 1}
                    step="1"
                    value={this.getIndexFromSensitivityVal(this.props.sensitivityVal)}
                    onChange={this.onSensitivityChange}
                    onMouseUp={this.onSensitivityChangeEnd}
                    onTouchEnd={this.onSensitivityChangeEnd}
                />
            </div>
        );
    }

    render() {
        return (
            <div>
                {this.renderSensitivitySettings()}
            </div>
        );
    }
}

export default SensitivitySetting;