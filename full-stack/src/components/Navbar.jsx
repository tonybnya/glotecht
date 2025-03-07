import ModalInfo from "./ModalInfo";

const Navbar = () => {
  const title = "Coding Challenges";
  const description =
    "By working through 100+ real-world challenges in React, JavaScript, and Python, I'm not just learning to code—I'm mastering the problem-solving skills, technical expertise, and best practices that make me a highly hireable Software Engineer. These challenges simulate every days tasks facing in startups, companies, and coding interviews, helping me build a portfolio of projects that showcase my ability to deliver scalable, efficient, and maintainable solutions. With hands-on experience in full-stack development, data structures, and algorithms, I'll stand out to employers as a versatile, confident, and adaptable engineer ready to tackle real-world problems and succeed in any team environment. I'm confident that my skills and experience will make me a valuable asset to any team, and I'm excited to apply my knowledge and passion for software development to real-world projects. 🚀";

  return (
    <nav className="text-white flex max-sm:flex-col items-center justify-between mx-20">
      <p className="text-3xl font-bold flex items-center gap-2">
        <img
          src="/challenge.svg"
          className="w-20 2-10 text-white"
          alt="challenge logo"
        />
        <span className="text-xl max-sm:text-sm tracking-tight">
          Coding
          <br />
          Challenges
        </span>
      </p>
      <ModalInfo title={title} description={description} />
    </nav>
  );
};

export default Navbar;
