const API_URL = "http://localhost:8000/api";

export const fetchChallenges = async () => {
  try {
    const response = await fetch(`${API_URL}/challenges/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching challenges:", error);
    throw error;
  }
};

export const updateChallenge = async (id, completed) => {
  try {
    const response = await fetch(`${API_URL}/challenges/${id}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ completed }),
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error updating challenge:", error);
    throw error;
  }
};
