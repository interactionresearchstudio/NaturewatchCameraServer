import React from 'react';
import Header from './Header'
import CameraFeed from './CameraFeed'

class Index extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            feedStatus: "active"
        };
    }
    componentDidMount() {
        setTimeout(() => {
            console.log("INFO: Feed status timeout.");
            this.setState({
                feedStatus: "inactive"
            });
        }, 60000);
    }

    render() {
        return(
            <div className="index">
                <Header/>
                <CameraFeed status={this.state.feedStatus}/>
            </div>
        );
    }
}

export default Index;
