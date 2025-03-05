import bg from "/bg.png";
import logo from "/challenge.svg";

const NoPage = () => {
  return (
    <div className="min-h-screen flex text-white">
      <div className="w-1/2 h-screen">
        <img
          src={bg}
          alt="Background illustration"
          className="h-full w-full object-cover"
        />
      </div>

      <div className="w-1/2 flex flex-col justify-between max-lg:justify-center items-center p-8 bg-black min-h-screen">
        <div className="flex flex-col items-center gap-3 mb-12">
          <img
            src={logo}
            className="h-12 w-12 max-lg:w-10 max-lg:h-10 text-primary"
          />
          <span className="text-4xl max-lg:text-lg font-bold text-primary tracking-tight">
            Coding Challenges
          </span>
        </div>

        <div className="text-center space-y-4 mb-12">
          <h1 className="text-4xl max-lg:text-lg font-semibold leading-none tracking-tight">
            Oops! You have
            <br />
            discovered a world not
            <br />
            found!
          </h1>
          <p className="text-lg max-lg:text-sm font-light leading-6 tracking-tight">
            Home is just a click away. Let&apos;s go back and
            <br />
            continue our challenges.
          </p>

          <button
            size="lg"
            className="px-6 py-2 rounded-md bg-white text-black hover:text-white hover:bg-[#602f32]"
          >
            <a
              href="/"
              className="uppercase font-bold"
              rel="noopener noreferrer"
              aria-label="Go to home page"
            >
              Go to Home
            </a>
          </button>
        </div>

        <div className="mt-12 text-[#8f7d5e] text-sm font-bold">
          <span>Error Code 404</span>
        </div>
      </div>
    </div>
  );
};

export default NoPage;
