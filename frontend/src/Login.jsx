import { useState } from "react";
import axios from "axios";
import Button from "./components/Button";

function Login({ setToken }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const login = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/api/token/", {
        username,
        password,
      });
      setToken(res.data.access);
    } catch (err) {
      alert("Login failed");
    }
  };

  return (
    <div className="flex flex-col align-middle min-h-screen min-w-screen items-center justify-center">
      <div className="m-8">
        <h1 className="text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-indigo-500 to-green-500 animate-gradient">
          GitDriller
        </h1>
      </div>
      <div className=" backdrop-blur-3xl border-2 border-dashed p-4 rounded-lg shadow-md ">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-200">
          Sign in to your account
        </h2>
        <form onSubmit={login} className="space-x-5 flex items-center">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-200"
            >
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your username"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-200"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your password"
            />
          </div>
          <div className="flex flex-col justify-end h-full">
            <Button
              type="submit"
              text="Login"
              onClick={login}
              disabled={!username || !password}
            />
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;
