import React from "react";

const Button = ({ text, onClick, disabled, type }) => {
  return (
    <div
      onClick={onClick}
      className="w-fit flex flex-col justify-center ml-auto"
    >
      <button
        disabled={disabled}
        type={type || "button"}
        className={`${
          disabled ? "group cursor-not-allowed" : "group cursor-pointer"
        } bg-slate-800 no-underline group relative shadow-2xl shadow-zinc-900 rounded-full p-px text-lg font-semibold text-white inline-block`}
      >
        <span className="absolute inset-0 overflow-hidden rounded-full">
          <span className="absolute inset-0 rounded-full bg-[image:radial-gradient(75%_100%_at_50%_0%,rgba(56,189,248,0.6)_0%,rgba(56,189,248,0)_75%)] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
        </span>
        <div className="relative flex space-x-2 items-center rounded-full bg-slate-900 py-3 px-8 ring-1 ring-white/10 ">
          <span>{text}</span>
          <svg
            fill="none"
            height="16"
            viewBox="0 0 24 24"
            width="16"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10.75 8.75L14.25 12L10.75 15.25"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
            />
          </svg>
        </div>
        <span className="absolute -bottom-0 left-[1.125rem] h-px w-[calc(100%-2.25rem)] bg-gradient-to-r from-emerald-400/0 via-emerald-400/90 to-emerald-400/0 transition-opacity duration-500 group-hover:opacity-40" />
      </button>
    </div>
  );
};

export default Button;
