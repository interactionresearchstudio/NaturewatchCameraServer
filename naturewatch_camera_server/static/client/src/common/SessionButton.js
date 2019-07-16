import React from 'react';
import {Button} from 'react-bootstrap';

class SessionButton extends React.Component {
    render() {
        return(
            <Button
                size="lg"
                className="startsession"
                onClick={this.props.onButtonClick}
                active={
                    this.props.sessionStatus === this.props.type
                }
                disabled={
                    this.props.sessionStatus !== "inactive" && this.props.sessionStatus !== this.props.type
                }
            >
                {this.props.text}
            </Button>
        )
    }
}

export default SessionButton;