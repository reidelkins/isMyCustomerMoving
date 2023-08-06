import React from "react";
import { Doughnut } from 'react-chartjs-2';
import { Stack } from '@mui/material';
import { Chart, CategoryScale, LinearScale, BarElement, ArcElement } from 'chart.js';
import PropTypes from 'prop-types';

import homeStyle from '../../theme/Home.module.css';

Chart.register(CategoryScale, LinearScale, BarElement, ArcElement);


const Speedometer = ({ title, needleValue}) => {
  const data = {
    labels: [],
    datasets: [
      {
        // label: dataLabel,
        data: [100],
        backgroundColor: (context) => {
          const { chart } = context;
          const { chartArea } = chart;
          if (!chartArea) {
            // This case happens on initial chart load
            return null;
          }
          if(context.dataIndex === 0){
            return getGradient(chart);
          } 
          return '#909090';
          
        },
        borderColor:[],
        borderWidth: 0,              
        circumference: 180,
        rotation: 270,
        redraw: true,
        needleValue      
      },
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
      },
      maintainAspectRatio: false,
      tooltip: {
        enabled: false,
      },                  
    },
    cutout: '65%',    
  };

  const guageNeedle = {
    id: 'guageNeedle',
    afterDatasetsDraw(chart) {
      const {ctx, data } = chart;

      ctx.save();
      const { needleValue } = data.datasets[0];
      const xCenter = chart.getDatasetMeta(0).data[0].x;
      const yCenter = chart.getDatasetMeta(0).data[0].y;
      const outerRadius = chart.getDatasetMeta(0).data[0].outerRadius - 10;
      const angle = Math.PI;

      // const dataTotal = data.datasets[0].data.reduce((a, b) => a + b, 0);
      const circumference = ((chart.getDatasetMeta(0).data[0].circumference) / Math.PI / data.datasets[0].data[0]) * needleValue;
      const needleValueAngle = circumference + 1.5;
      ctx.translate(xCenter, yCenter);
      ctx.rotate(angle * needleValueAngle);

      // needle
      ctx.beginPath();
      ctx.strokeStyle = '#000000';
      ctx.fillStyle = '#000000';      
      ctx.lineWidth = 5;
      ctx.moveTo(0-7, 0);
      ctx.lineTo(0, -outerRadius);
      ctx.lineTo(0+7, 0);
      ctx.stroke();

      // dot
      ctx.restore();
      ctx.strokeStyle = '#ff0000';
      ctx.beginPath();
      ctx.arc(xCenter, yCenter, 10, angle * 0, angle * 2, false);
      ctx.fill();
    }
  }
  // const guageChartText = {
  //   id: 'guageChartText',
  //   afterDatasetsDraw(chart, args, pluginOptions) {
  //     const {ctx, data, chartArea: {top, bottom, left, right, width, height}, scales: {r}} = chart;
  //     ctx.save();
  //     const xCoor = chart.getDatasetMeta(0).data[0].x;
  //     const yCoor = chart.getDatasetMeta(0).data[0].y;

  //     ctx.fillRect(xCoor, yCoor, 400, 1);

  //     ctx.font = '20px sans-serif';
  //     ctx.fillStyle = '#000000';
  //     ctx.testBaseLine = 'top';
  //     ctx.textAlign = 'left';
  //     ctx.fillText('0%', left, yCoor + 20);

  //     ctx.textAlign = 'right';
  //     ctx.fillText('100%', right, yCoor + 20);

  //     ctx.font = '150px sans-serif';
  //     ctx.textAlign = 'center';
  //     ctx.fillText('7%', xCoor, yCoor);
  //   }
  // }  

  function getGradient(chart){
    const {ctx, chartArea: {left, right}} = chart;
    const gradient = ctx.createLinearGradient(left, 0, right, 0);
    gradient.addColorStop(0, 'rgba(255, 0, 0)');
    gradient.addColorStop(0.5, 'rgba(255, 255, 0)');
    gradient.addColorStop(1, 'rgb(0, 128, 0)');
    return gradient;
  }  
  return (
    <div className={homeStyle.main}>
      <Stack spacing={-5} direction="column" alignItems="center">
        <h1>{title}</h1>
        <Doughnut
          data={data}
          options={options}
          plugins={[guageNeedle]}    
        />
      </Stack>
    </div>
  );  
  
};

Speedometer.propTypes = {
  title: PropTypes.string.isRequired,
  needleValue: PropTypes.number.isRequired,
  // dataLabel: PropTypes.string.isRequired,  
};

export default Speedometer;

// export const StateRevenueDonut = () => (
//   <div className={homeStyle.main}>
//     <h2>Revenue by City</h2>
//     <Pie data={data} options={options} />
//   </div>
// );
