import { useState, useEffect } from "react";
import CardChallenge from "../components/CardChallenge";
import Spinner from "../components/Spinner";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

console.log("API_URL:", API_URL);

const Home = () => {
  const [challenges, setChallenges] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchChallenges = async () => {
      setIsLoading(true);
      setError("");

      try {
        const response = await fetch(`${API_URL}/challenges/`, {
          method: "GET",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          mode: "cors", // Add this
          credentials: "same-origin",
          // credentials: "omit", // Change from 'include' to 'omit'
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data || data.length === 0) {
          throw new Error("No challenges found");
        }

        setChallenges(data);
      } catch (error) {
        console.error("Error:", error);
        setError(`Failed to fetch challenges: ${error.message}`);
        setChallenges([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChallenges();
  }, []);

  return (
    <div className="bg-[#030713] text-white min-h-screen px-4 sm:px-6 lg:px-20 mt-10">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 p-2 place-items-center bg-[#1C202A] rounded-md">
        {isLoading ? (
          <Spinner className="text-center mx-auto" />
        ) : error ? (
          <p className="text-red-900 text-center mx-auto">{error}</p>
        ) : (
          challenges.map((challenge) => (
            <CardChallenge
              key={challenge.id}
              icon={challenge.icon}
              title={challenge.title}
              description={challenge.description}
              tags={challenge.tags}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default Home;
