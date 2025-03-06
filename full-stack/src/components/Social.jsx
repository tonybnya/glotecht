import { FileCode, Github, Linkedin } from "lucide-react";

const Social = () => {
  return (
    <ul className="flex items-center justify-center gap-2 text-sm font-medium">
      <li>
        <a
          href="https://tonybnya-portfolio.onrender.com/"
          target="_blank"
          className="text-gray-500 hover:text-white"
        >
          <FileCode />
        </a>
      </li>
      <li>
        <a
          href="https://github.com/tonybnya"
          target="_blank"
          className="text-gray-500 hover:text-white"
        >
          <Github />
        </a>
      </li>
      <li>
        <a
          href="https://linkedin.com/in/tonybnya"
          target="_blank"
          className="text-gray-500 hover:text-white"
        >
          <Linkedin />
        </a>
      </li>
      <li>
        <a
          href="https://x.com/tonybnya"
          target="_blank"
          className="text-gray-500 hover:text-white"
        >
          <svg
            className="w-5 h-5 fill-current"
            role="img"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
          >
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
        </a>
      </li>
    </ul>
  );
};

export default Social;
