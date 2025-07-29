import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const getStocks = async (market) => {
  const res = await axios.get(`${BASE_URL}/stocks/${market}`);
  return res.data;
};

export const analyzeStock = async (symbol) => {
  const res = await axios.get(`${BASE_URL}/analyze/${symbol}`);
  return res.data;
};

export const getFundamentals = async (symbol) => {
  const res = await axios.get(`${BASE_URL}/fundamentals/${symbol}`);
  return res.data;
};
