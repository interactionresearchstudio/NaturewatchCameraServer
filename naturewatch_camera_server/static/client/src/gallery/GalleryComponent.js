import React from 'react';
import {Container, Row, Col} from 'react-bootstrap';
import { Link } from 'react-router-dom';
//import Gallery from 'react-grid-gallery';
import axios from 'axios';
import Header from '../common/Header';
import ContentTypeSelector from './ContentTypeSelector';
import ContentSelect from './ContentSelect';
import GalleryGrid from './GalleryGrid';

class GalleryComponent extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.handleBackButton = this.handleBackButton.bind(this);
        this.onContentTypeChange = this.onContentTypeChange.bind(this);
        this.onSelectStart = this.onSelectStart.bind(this);
        this.onDelete = this.onDelete.bind(this);
        this.onDeleteAll = this.onDeleteAll.bind(this);
        this.onClearSelection = this.onClearSelection.bind(this);
        this.onContentSelect = this.onContentSelect.bind(this);

        this.state = {
            content: [],
            showingVideos: false,
            isSelectActive: false
        }

    }

    componentDidMount() {
        this.getPhotos();
    }

    getPhotos() {
        axios.get('/data/photos')
            .then((res) => {
                let photoArray = [];
                let i = 0;
                res.data.forEach((photo) => {
                    photoArray.push({
                        src: '/data/photos/' + photo,
                        thumbnail: '/data/photos/thumb_' + photo,
                        index: i,
                        selected: false
                    });
                    i++;
                });
                this.setState( {
                    content: photoArray
                }, () => {
                    console.log(this.state.content)
                });
        });
    }

    getVideos() {
        axios.get('/data/videos')
            .then((res) => {
                let videoArray = [];
                let i = 0;
                res.data.forEach((video) => {
                    videoArray.push({
                        src: '/data/videos/' + video,
                        thumbnail: '/data/videos/thumb_' + video.substr(0, video.lastIndexOf('.')) + '.jpg',
                        index: i,
                        selected: false
                    });
                    i++;
                });
                this.setState( {
                    content: videoArray
                }, () => {
                    console.log(this.state.content)
                });
            });
    }

    handleBackButton() {
        this.context.router.history.push('/');
    }

    onContentTypeChange() {
        if (this.state.showingVideos) {
            this.getPhotos();
            this.setState({
                showingVideos: false
            });
        } else {
            this.getVideos();
            this.setState({
                showingVideos: true
            });
        }
    }

    onSelectStart() {
        this.setState({
            isSelectActive: true
        });
    }

    onDelete() {
        let tempContent = this.state.content;
        for (let i=0; i<tempContent.length; i++) {
            if (tempContent[i].selected) {
                axios.delete(tempContent[i].src)
                    .then((res) => {
                        axios.delete(tempContent[i].thumbnail)
                            .then((_res) => {
                                console.log("Deleted " + tempContent[i].src);
                                if (this.state.showingVideos) {
                                    this.getVideos();
                                } else {
                                    this.getPhotos();
                                }
                            });
                    });
            }
        }
    }

    onDeleteAll() {
        let tempContent = this.state.content;
        for (let i=0; i<tempContent.length; i++) {
            axios.delete(tempContent[i].thumbnail)
                .then((res) => {
                    axios.delete(tempContent[i].src)
                        .then((_res) => {
                            console.log("Deleted " + tempContent[i].src);
                            if (this.state.showingVideos) {
                                this.getVideos();
                            } else {
                                this.getPhotos();
                            }
                        });
                });
        }

    }

    onClearSelection() {
        this.setState({
            isSelectActive: false
        }, () => {
            if (this.state.showingVideos) {
                this.getVideos();
            } else {
                this.getPhotos();
            }
        })
    }

    onContentSelect(clickedItem) {
        console.log(clickedItem.index);
        let tempContent = this.state.content;
        for (let i=0; i<tempContent.length; i++) {
            if (tempContent[i].index === clickedItem.index) {
                tempContent[i].selected = !tempContent[i].selected;
                break;
            }
        }
        this.setState({
            content: tempContent
        }, () => {
            console.log(this.state.content);
        });
    }

    render() {
        return (
            <Container>
                <Row>
                    <Col>
                        <Header/>
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <ContentTypeSelector onToggle={this.onContentTypeChange}/>
                    </Col>
                </Row>
                <Row>
                    <Col xs={6}>
                        <Link to="/" className="btn btn-secondary">Back</Link>
                    </Col>
                    <Col xs={6}>
                        <ContentSelect
                            onSelectStart={this.onSelectStart}
                            onDelete={this.onDelete}
                            onDeleteAll={this.onDeleteAll}
                            onClearSelection={this.onClearSelection}
                            isSelectActive={this.state.isSelectActive}
                        />
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <GalleryGrid
                            content={this.state.content}
                            onContentClick={this.onContentSelect}
                            isSelectActive={this.state.isSelectActive}
                        />
                    </Col>
                </Row>
            </Container>
        );
    }
}

export default GalleryComponent;