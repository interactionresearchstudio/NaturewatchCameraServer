import React from 'react';
import { Button } from 'react-bootstrap';

class ContentSelect extends React.Component {
    render() {
        return(
            <div className="content-select">
                <Button
                    variant="primary"
                >
                    Select
                </Button>
            </div>
        );
    }
}

export default ContentSelect;