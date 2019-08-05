import React from 'react';

class ContentTypeSelector extends React.Component {
    constructor(props) {
        super(props);

        this.onToggle = this.onToggle.bind(this);

        this.state = {
            toggleActive: false
        };
    }

    onToggle() {
        this.setState( {
            toggleActive: !this.state.toggleActive
        });
    }

    render() {
        return (
            <div className="content-type-selector float-right">
                <p>Photo</p>
                <label className="switch">
                    <input type="checkbox"/>
                    <span className="slider round"></span>
                </label>
                <p>Video</p>
            </div>
        );
    }
}

export default ContentTypeSelector;