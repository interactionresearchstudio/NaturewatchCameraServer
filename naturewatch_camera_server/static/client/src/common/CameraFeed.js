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
               <h2>Preview paused to save power</h2>
           </div>
        )
    }

    closingFeed(status) {
        return (
            <div id="closing-feed">
                <h2>Preview ends in {status}</h2>
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