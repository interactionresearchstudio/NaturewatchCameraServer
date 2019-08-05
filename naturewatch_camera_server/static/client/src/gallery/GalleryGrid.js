import React from 'react';

class GalleryGrid extends React.Component {
    renderItems() {
        return this.props.items.map((item, i) => {
            return (

            );
        });
    }

    render() {
        return (
            <div className="gallery-grid">
                {this.renderItems()}
            </div>
        );
    }
}

export default GalleryGrid;