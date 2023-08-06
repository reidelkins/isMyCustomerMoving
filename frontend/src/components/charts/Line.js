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
import PropTypes from 'prop-types';
import homeStyle from '../../theme/Home.module.css';


ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler, Legend);


const LineChart = ({ title, keys, values, dataLabel, height }) => {
  const labels = keys;
  const data = {
  labels,
  datasets: [
    {
      fill: true,
      data: values,      
      borderColor: 'rgb(107, 128, 104)',
      backgroundColor: 'rgba(107, 128, 104, 0.5)',
      label: dataLabel,
    },
    // {
    //   label: 'Dataset 2',
    //   data: [28, 48, 40, 19, 86, 27, 90],
    //   borderColor: 'rgb(53, 162, 235)',
    //   backgroundColor: 'rgba(53, 162, 235, 0.5)',
    // },
  ],
};
  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
        text: title,
        font: {
          size: 20,
        },
      },
    },
    scales: {
      y: {
        min: 0,
        ticks: {
          precision: 0
        }
      }
    }
  };
  return(
    <div className={homeStyle.main} style={{ height }}>
      <h1>{title}</h1>
      <Line options={options} data={data} />
    </div>
  );
};

LineChart.propTypes = {
  title: PropTypes.string.isRequired,
  keys: PropTypes.arrayOf(PropTypes.string).isRequired,
  values: PropTypes.arrayOf(PropTypes.number).isRequired,
  dataLabel: PropTypes.string.isRequired,
  height: PropTypes.string.isRequired,
};

export default LineChart;
