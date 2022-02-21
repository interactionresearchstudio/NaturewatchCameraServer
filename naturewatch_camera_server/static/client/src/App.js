import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route } from "react-router-dom";
import Index from "./common/Index";
import Footer from './common/Footer';
import GalleryComponent from "./gallery/GalleryComponent";

function App() {
    return (
        <div className="App">
            <Router>
                <Route path="/" exact component={Index} />
                <Route path="/gallery" exact component={GalleryComponent} />
            </Router>
            <Footer />
        </div>
    );
}

export default App;
