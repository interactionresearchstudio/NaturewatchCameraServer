import React from 'react';
import {Button} from 'react-bootstrap';

class SessionButton extends React.Component {
    constructor(props) {
        super(props);

        this.handleClick = this.handleClick.bind(this);
    }

    renderText() {
        if (this.props.sessionStatus === this.props.type) {
            return (
                <span>{"Stop " + this.props.type + " capture"}</span>
            );
        } else {
            return (
                <span>{"Start " + this.props.type + " capture"}</span>
            );
        }
    }

    handleClick() {
        this.props.onButtonClick(this.props.type);
    }

    render() {
        return(
            <Button
                size="lg"
                className="startsession"
                onClick={this.handleClick}
                active={
                    this.props.sessionStatus === this.props.type
                }
                disabled={
                    this.props.sessionStatus !== "inactive" && this.props.sessionStatus !== this.props.type
                }
            >
                {this.renderText()}
            </Button>
        )
    }
}

export default SessionButton;