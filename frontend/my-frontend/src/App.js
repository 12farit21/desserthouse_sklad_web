import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";
import Home from "./pages/home/Home";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/desserthouse_sklad_web/" element={<Home/>}/>

      </Routes>
    </BrowserRouter>
  );
}

export default App;
