import axios from "axios";

// Dynamic base URL - use environment variable in production, localhost in development
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const getStocks = async (market) => {
  const res = await axios.get(`${BASE_URL}/stocks`);
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

export const getLiveSignals = async () => {
  try {
    const res = await axios.get(`${BASE_URL}/api/v1/live-top-signals`);
    return {
      success: true,
      data: res.data,
      status: res.status,
    };
  } catch (error) {
    if (error.response?.status === 202) {
      // Analysis in progress
      return {
        success: false,
        analyzing: true,
        progress: error.response.data.detail?.progress || 0,
        message: error.response.data.detail?.message || "Analysis in progress",
        estimatedTime:
          error.response.data.detail?.estimated_time || "2-3 minutes",
        checkAgainIn:
          error.response.data.detail?.check_again_in || "30 seconds",
      };
    }
    throw error;
  }
};

export const getAnalysisStatus = async () => {
  const res = await axios.get(`${BASE_URL}/api/v1/analysis-status`);
  return res.data;
};

export const forceAnalysis = async () => {
  const res = await axios.post(`${BASE_URL}/api/v1/force-analysis`);
  return res.data;
};

export const checkHealth = async () => {
  const res = await axios.get(`${BASE_URL}/health`);
  return res.data;
};
