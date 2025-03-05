import Social from "./Social";

const Footer = () => {
  return (
    <footer className="p-8">
      <div className="mx-auto max-w-screen-xl flex flex-col items-center justify-center gap-2">
        <Social />
        <span className="text-sm text-gray-500">
          © {new Date().getFullYear()} <span>•</span> All Rights Reserved{" "}
          <span>•</span>
        </span>
      </div>
    </footer>
  );
};

export default Footer;
