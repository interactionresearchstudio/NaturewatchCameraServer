import React from 'react';
import { Button, ButtonGroup } from 'react-bootstrap';
import PropTypes from 'prop-types';

class ContentSelect extends React.Component {
    renderButtons() {
        if (this.props.isSelectActive) {
            return this.renderDeleteButtons();
        }
        else {
            return this.renderSelectButton();
        }
    }

    renderSelectButton() {
        return(
            <Button variant="primary" onClick={this.props.onSelectStart}>Select</Button>
        );
    }

    renderDeleteButtons() {
        return(
            <ButtonGroup aria-label="delete">
                <Button variant="primary" onClick={this.props.onDeleteAll}>Delete All</Button>
                <Button variant="primary" onClick={this.props.onDelete}>Delete</Button>
                <Button variant="primary" onClick={this.props.onClearSelection}>Cancel</Button>
            </ButtonGroup>
        );
    }

    render() {
        return(
            <div className="content-select">
                {this.renderButtons()}
            </div>
        );
    }
}

ContentSelect.propTypes = {
    isSelectActive: PropTypes.bool.isRequired,
    onSelectStart: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    onDeleteAll: PropTypes.func.isRequired,
    onClearSelection: PropTypes.func.isRequired
};

export default ContentSelect;