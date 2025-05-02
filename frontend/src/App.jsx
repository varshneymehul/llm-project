import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [text, setText] = useState("");
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/hello/")
      .then((res) => {
        console.log(res.data.message);
        setText(res.data.message);
      })
      .catch((err) => console.error(err));
  }, []);

  return (
    <>
      <div className="">
        <h1 className="font-bold text-7xl">Git Repository Analysis</h1>
        {text && <div>{text}</div>}
      </div>
    </>
  );
}

export default App;
