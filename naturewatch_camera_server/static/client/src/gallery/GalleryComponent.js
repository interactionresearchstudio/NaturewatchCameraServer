import React from 'react';
import {Container, Row, Col} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import axios from 'axios';
import FileDownload from 'js-file-download';
import Header from '../common/Header';
import ContentTypeSelector from './ContentTypeSelector';
import ContentDelete from './ContentDelete';
import GalleryGrid from './GalleryGrid';
import ContentDownload from "./ContentDownload";

class GalleryComponent extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.handleBackButton = this.handleBackButton.bind(this);
        this.onContentTypeChange = this.onContentTypeChange.bind(this);
        this.onSelectStart = this.onSelectStart.bind(this);
        this.onDelete = this.onDelete.bind(this);
        this.onDeleteAll = this.onDeleteAll.bind(this);
        this.onDownload = this.onDownload.bind(this);
        this.onDownloadAll = this.onDownloadAll.bind(this);
        this.onClearSelection = this.onClearSelection.bind(this);
        this.onContentSelect = this.onContentSelect.bind(this);
        this.downloadPaths = this.downloadPaths.bind(this);

        this.state = {
            content: [],
            showingVideos: false,
            isSelectActive: false,
            selectType: "none",
            isDownloading: false,
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

    onSelectStart(type) {
        this.setState({
            selectType: type
        });
    }

    onDelete() {
        let tempContent = this.state.content;
        for (let i=0; i<tempContent.length; i++) {
            if (tempContent[i].selected) {
                axios.delete(tempContent[i].src)
                    .then((res) => {
                        console.log("Deleted " + tempContent[i].src);
                        if (this.state.showingVideos) {
                            this.getVideos();
                        } else {
                            this.getPhotos();
                        }
                    });
            }
        }
    }

    onDeleteAll() {
        let tempContent = this.state.content;
        for (let i=0; i<tempContent.length; i++) {
            axios.delete(tempContent[i].src)
                .then((_res) => {
                    console.log("Deleted " + tempContent[i].src);
                    if (this.state.showingVideos) {
                        this.getVideos();
                    } else {
                        this.getPhotos();
                    }
                });
        }

    }

    onDownloadAll() {
        this.setState({isDownloading: true});
        axios({
            url: this.state.showingVideos ? '/data/download/videos.zip' : '/data/download/photos.zip',
            method: 'GET',
            responseType: 'blob'
        }).then((res) => {
            FileDownload(res.data, this.state.showingVideos ? 'videos.zip' : 'photos.zip');
            console.log("Downloaded all content.");
            this.setState({isDownloading: false});
        }).catch((err) => {
            console.error(err);
            this.setState({isDownloading: false});
        });
    }

    onDownload() {
        this.setState({isDownloading: true});
        let tempContent = this.state.content;
        let paths = [];
        tempContent.forEach((c) => {
            if (c.selected)
                paths.push(c.src.substr(c.src.lastIndexOf('/') + 1));
        });
        console.log(paths);
        this.downloadPaths(paths);
    }

    downloadPaths(paths) {
        axios({
            url: this.state.showingVideos ? '/data/download/videos.zip' : '/data/download/photos.zip',
            method: 'POST',
            responseType: 'blob',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                paths: paths
            }
        }).then((res) => {
            FileDownload(res.data, this.state.showingVideos ? 'videos.zip' : 'photos.zip');
            console.log("Downloaded content.");
            this.setState({isDownloading: false});
        }).catch((err) => {
            console.error(err);
            this.setState({isDownloading: false});
        });
    }

    onClearSelection() {
        this.setState({
            selectType: 'none'
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
                        <ContentDelete
                            onSelectStart={this.onSelectStart}
                            onDelete={this.onDelete}
                            onDeleteAll={this.onDeleteAll}
                            onClearSelection={this.onClearSelection}
                            isSelectActive={this.state.selectType === 'delete'}
                        />
                        <ContentDownload
                            isSelectActive={this.state.selectType === 'download'}
                            onSelectStart={this.onSelectStart}
                            onDownload={this.onDownload}
                            onDownloadAll={this.onDownloadAll}
                            onClearSelection={this.onClearSelection}
                            isDownloading={this.state.isDownloading}
                        />
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <GalleryGrid
                            content={this.state.content}
                            onContentClick={this.onContentSelect}
                            isSelectActive={this.state.selectType !== 'none'}
                        />
                    </Col>
                </Row>
            </Container>
        );
    }
}

export default GalleryComponent;