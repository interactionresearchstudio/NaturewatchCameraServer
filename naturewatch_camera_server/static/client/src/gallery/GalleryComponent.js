import React from 'react';
import {Container, Row, Col} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import Gallery from 'react-grid-gallery';
import axios from 'axios';
import Header from '../common/Header';
import ContentTypeSelector from './ContentTypeSelector';
import ContentSelect from './ContentSelect';

class GalleryComponent extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.handleBackButton = this.handleBackButton.bind(this);

        this.state = {
            photos: [],
            videos: [],
            showingVideos: false
        }

    }

    componentDidMount() {
        axios.get('/data/photos')
            .then((res) => {
                var photoArray = [];
                res.data.forEach((photo) => {
                    photoArray.push({
                        src: '/data/photos/' + photo,
                        thumbnail: '/data/photos/' + photo,
                        thumbnailWidth: 100,
                        thumbnailHeight: 100
                    });
                });
                this.setState( {
                    photos: photoArray
                }, () => {
                    console.log(this.state.photos)
                });
        });
    }

    handleBackButton() {
        this.context.router.history.push('/');
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
                        <ContentTypeSelector/>
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
                    <Gallery images={this.state.photos}/>
                </Row>
            </Container>
        );
    }
}

export default GalleryComponent;