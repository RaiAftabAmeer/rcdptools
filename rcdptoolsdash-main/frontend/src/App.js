import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard3D from "./components/Dashboard3D";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard3D />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
