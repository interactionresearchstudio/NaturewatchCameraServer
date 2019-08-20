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

        this.state = {
            content: [],
            showingVideos: false
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
                        index: i
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
                        index: i
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
                        <ContentSelect/>
                    </Col>
                </Row>
                <Row>
                    <GalleryGrid content={this.state.content}/>
                </Row>
            </Container>
        );
    }
}

export default GalleryComponent;