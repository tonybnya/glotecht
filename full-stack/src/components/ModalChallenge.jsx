/* eslint-disable react/prop-types */
import { useState } from "react";
import { Check, Copy, ExternalLink, Github } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { nord } from "react-syntax-highlighter/dist/esm/styles/prism";

const ModalChallenge = ({ challenge }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(challenge.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      onClick={() => setIsOpen(true)}
      className="cursor-pointer bg-[#030713] w-full p-2 rounded-md border border-[#2C2C2C] text-center hover:bg-[#1C202A]"
    >
      {challenge.completed ? (
        <div className="flex items-center justify-between gap-2 text-[#D0D5DB]">
          <span className="text-[#D0D5DB] max-lg:text-sm">
            {challenge.id.toString().padStart(3, "0")} - {challenge.title}
          </span>
          <span className="text-green-500 text-md">✓</span>
        </div>
      ) : (
        <div className="flex items-center justify-between gap-2">
          <span className="text-[#D0D5DB] max-lg:text-sm">
            {challenge.id.toString().padStart(3, "0")} - {challenge.title}
          </span>
          <span className="text-red-500">✕</span>
        </div>
      )}
      {isOpen && (
        <div className="fixed inset-0 px-2 z-10 overflow-hidden flex items-center justify-center">
          <div
            onClick={() => setIsOpen(false)}
            className="absolute inset-0 bg-[#030713] opacity-95"
          ></div>

          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-[#030713] rounded-md shadow-2xl shadow-white/50 drop-shadow-2xl w-[95%] md:w-[85%] lg:w-[70%] h-[90%] md:h-[80%] flex flex-col"
          >
            <div className="bg-black text-white px-4 py-2 flex justify-center rounded-tl-md rounded-tr-md">
              <h2 className="text-lg font-bold tracking-tight">
                Challenge {challenge.id}: {challenge.title}
              </h2>
            </div>

            <div className="p-4 overflow-y-auto flex-grow flex flex-col lg:flex-row gap-6 justify-between">
              <div className="text-left w-full lg:w-2/3">
                <h3 className="pb-4 text-gray-300">Description:</h3>
                <p className="font-bold tracking-normal text-justify text-sky-500/80">
                  {challenge.description}
                </p>
                {challenge.stack && (
                  <div className="mt-4">
                    <h3 className="pb-4 text-gray-300">Tech Stack:</h3>
                    <ul className="text-white tracking-normal text-justify flex flex-col gap-2">
                      {challenge.stack.map((item, index) => (
                        <li
                          key={index}
                          className="border border-[#10141F] p-2 text-red-950"
                        >
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {challenge.completed && (
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center justify-between gap-2 pt-4">
                      <span>{challenge.title}</span>
                      <span className="text-green-500 text-md">✓</span>
                    </div>
                    <a
                      href="https://tonybnya-portfolio.onrender.com/"
                      target="_blank"
                    >
                      <ExternalLink />
                    </a>
                    <a
                      href="https://github.com/tonybnya/portfolio"
                      target="_blank"
                    >
                      <Github />
                    </a>
                  </div>
                )}
              </div>
              <div className="flex flex-col items-center w-full lg:w-2/3">
                <h3 className="pb-4 text-gray-300">Starter Code Snippet:</h3>
                <div className="relative rounded-md bg-[#10141F] text-white">
                  <div className="flex items-center justify-between px-4 py-2 bg-[#2C2C2C] rounded-t-md">
                    <span className="text-sm text-gray-400">jsx</span>
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-1 text-sm text-gray-400 hover:text-white"
                    >
                      {copied ? (
                        <Check className="w-4 h-4" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                      {copied ? "Copied!" : "Copy"}
                    </button>
                  </div>
                  <SyntaxHighlighter
                    language="jsx"
                    style={nord}
                    customStyle={{
                      margin: 0,
                      padding: "1rem",
                      background: "#10141F",
                      borderBottomLeftRadius: "0.375rem",
                      borderBottomRightRadius: "0.375rem",
                    }}
                  >
                    {challenge.snippet}
                  </SyntaxHighlighter>
                </div>
              </div>
            </div>

            <div className="px-4 py-2 flex justify-end">
              <button
                onClick={() => setIsOpen(false)}
                className="font-bold rounded-md text-center text-white bg-black hover:bg-white hover:text-black px-4 py-3 mx-auto cursor-pointer"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModalChallenge;
