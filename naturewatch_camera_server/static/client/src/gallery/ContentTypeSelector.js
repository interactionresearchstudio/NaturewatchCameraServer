import React from 'react';
import PropTypes from 'prop-types';

class ContentTypeSelector extends React.Component {
    render() {
        return (
            <div className="content-type-selector float-right">
                <p>Photo</p>
                <label className="switch">
                    <input type="checkbox" onClick={this.props.onToggle}/>
                    <span className="slider round"></span>
                </label>
                <p>Video</p>
            </div>
        );
    }
}

ContentTypeSelector.propTypes = {
    onToggle: PropTypes.func.isRequired
};

export default ContentTypeSelector;