import React from 'react';
import PropTypes from 'prop-types';
import {Modal, Button} from 'react-bootstrap';
import LazyLoad from 'react-lazy-load';
import {CheckCircle, Cancel} from '@material-ui/icons'
import {GridList, GridListTile} from "@material-ui/core";

class GalleryGrid extends React.Component {
    constructor(props) {
        super(props);

        this.handleThumbnailClick = this.handleThumbnailClick.bind(this);
        this.handleModalExit = this.handleModalExit.bind(this);

        this.state = {
            activeContent: "",
            isModalShowing: false
        };
    }

    handleThumbnailClick(item) {
        if (this.props.isSelectActive) {
            this.props.onContentClick(item);
        } else {
            this.setState({
                activeContent: item.src,
                isModalShowing: true
            }, () => {
                console.log("Updated active content with value " + item.src);
            });
        }
    }

    handleModalExit() {
        this.setState({
            activeContent: "",
            isModalShowing: false
        });
    }

    renderItem(item, index) {
        return (
            <GridListTile key={index} cols={1}>
            <div key={item.thumbnail} className="gallery-thumbnail">
                <LazyLoad>
                    <img alt="Captured by Naturewatch Camera" src={item.thumbnail} onClick={this.handleThumbnailClick.bind(this, item)}/>
                </LazyLoad>
                {this.renderSelectIcon(item)}
            </div>
            </GridListTile>
        );

    }

    renderSelectIcon(item) {
        if (this.props.isSelectActive) {
            if (item.selected) {
                return (
                    <CheckCircle/>
                );
            } else {
                return null;
            }
        }
    }

    renderModal() {
        return (
            <Modal
                show={this.state.isModalShowing}
                size="lg"
                aria-labelledby="contained-modal-title-vcenter"
                centered
                className="modal-gallery-content"
                onHide={this.handleModalExit}
            >
                <Modal.Body>
                    {this.renderModalContent()}
                </Modal.Body>
                <Modal.Footer>
                    {this.state.activeContent.endsWith(".jpg") &&
                        <p className="mr-auto">Press and hold photo to download.</p>
                    }
                    <Button variant="primary" onClick={this.handleModalExit}>
                        <Cancel/>
                    </Button>
                </Modal.Footer>
            </Modal>
        );
    }

    renderModalContent() {
        if (this.state.activeContent.endsWith(".mp4")) {
            return (
                <video controls>
                    <source src={this.state.activeContent} type="video/mp4"/>
                    Your browser does not support the video tag.
                </video>
            );
        } else {
            return (
                <img alt="" src={this.state.activeContent}/>
            );
        }
    }

    render() {
        return (
            <div className="gallery-grid">
                <GridList
                    cellHeight={100}
                    className={"gallery-grid-list"}
                    cols={3}
                >
                    {this.props.content.map((item, index) => this.renderItem(item, index))}
                </GridList>
                {this.renderModal()}
            </div>
        );
    }
}

GalleryGrid.propTypes = {
    content: PropTypes.arrayOf(PropTypes.object).isRequired,
    onContentClick: PropTypes.func.isRequired,
    isSelectActive: PropTypes.bool.isRequired
};

export default GalleryGrid;