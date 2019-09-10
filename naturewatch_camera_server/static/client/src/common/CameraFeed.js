import React from 'react';

class CameraFeed extends React.Component {

    renderFeed(props) {
        const status = props.status;
        if (status === "active") {
            return this.activeFeed()
        } else if (status === "inactive") {
            return this.inactiveFeed()
        } else {
            return this.closingFeed(status)
        }
    }

    activeFeed() {
        return (
            <img src="/api/feed" alt="Camera feed"/>
        );
    }

    inactiveFeed() {
        return (
           <div id="inactive-feed">
               <span onClick={this.props.onClick}><h2>Preview paused <br/>to save power. Tap to refresh.</h2></span>
           </div>
        )
    }

    closingFeed(status) {
        return (
            <div id="closing-feed">
                <span><h2>Preview ends <br/>in {status}</h2></span>
            </div>
        )
    }

    render() {
        return(
            <div className="feed">
                {this.renderFeed(this.props)}
            </div>
        );
    }
}

export default CameraFeed;