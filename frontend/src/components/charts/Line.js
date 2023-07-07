import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import homeStyle from '../../theme/Home.module.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler, Legend);

const options = {
  responsive: true,
  plugins: {
    legend: {
      display: false,
    },
    title: {
      display: false,
      text: 'Attributed Revenue',
      font: {
        size: 20,
      },
    },
  },
};

const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];

const data = {
  labels,
  datasets: [
    {
      fill: true,
      data: [25317, 19950, 14650, 24234, 31764, 37765, 8619],
      borderColor: 'rgb(107, 128, 104)',
      backgroundColor: 'rgba(107, 128, 104, 0.5)',
    },
    // {
    //   label: 'Dataset 2',
    //   data: [28, 48, 40, 19, 86, 27, 90],
    //   borderColor: 'rgb(53, 162, 235)',
    //   backgroundColor: 'rgba(53, 162, 235, 0.5)',
    // },
  ],
};

const LineChart = () => {
  return (
    <div className={homeStyle.main}>
      <h2>Attributed Revenue</h2>
      <Line options={options} data={data} />
    </div>
  );
};

export default LineChart;
