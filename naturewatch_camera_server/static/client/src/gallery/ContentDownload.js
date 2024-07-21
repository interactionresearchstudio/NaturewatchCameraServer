import React from 'react';
import { Button, ButtonGroup } from 'react-bootstrap';
import PropTypes from 'prop-types';

class ContentDownload extends React.Component {
    renderButtons() {
        if (this.props.isSelectActive) {
            return this.renderDownloadButtons();
        }
        else {
            return this.renderDownloadButton();
        }
    }

    renderDownloadButton() {
        return(
            <Button variant="primary" onClick={() => {this.props.onSelectStart('download')}}>Download</Button>
        );
    }

    renderDownloadButtons() {
        return(
            <ButtonGroup aria-label="download">
                <Button variant="primary" disabled={this.props.isDownloading} onClick={this.props.onDownloadAll}>Download All</Button>
                <Button variant="primary" disabled={this.props.isDownloading} onClick={this.props.onDownload}>Download Selected</Button>
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

ContentDownload.propTypes = {
    isSelectActive: PropTypes.bool.isRequired,
    onSelectStart: PropTypes.func.isRequired,
    onDownload: PropTypes.func.isRequired,
    onDownloadAll: PropTypes.func.isRequired,
    onClearSelection: PropTypes.func.isRequired
};

export default ContentDownload;