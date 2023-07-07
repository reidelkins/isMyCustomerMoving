import { Doughnut, Pie } from 'react-chartjs-2';

import { Chart, CategoryScale, LinearScale, BarElement, ArcElement } from 'chart.js';
import homeStyle from '../../theme/Home.module.css';

Chart.register(CategoryScale, LinearScale, BarElement, ArcElement);
const labels = [
  'Sevierville',
  'Cosby',
  'Knoxville',
  'Riceville',
  'Hixson',
  'Rockford',
  'New Tazewell',
  'Thorn Hill',
  'Lenoir City',
  'White Pine',
  'Morristown',
  'Powell',
  'Cleveland',
  'Dandridge',
  'Tallassee',
  'Madisonville',
  'Loudon',
  'Dalton',
  'Spring City',
  'Copperhill',
  'Philadelphia',
  'Louisville',
  'Georgetown',
  'Walland',
  'Oak Ridge',
  'Jefferson City',
  'Parrottsville',
  'Vonore',
  'Andersonville',
  'Calhoun',
  'Ooltewah',
  'Rutledge',
  'Deer Lodge',
  'Pigeon Forge',
  'Greenback',
  'Rogersville',
  'Newport',
  'Clinton',
  'Kyles Ford',
  'Kodak',
  'Mooresburg',
  'Maryville',
  'Bybee',
  'Signal Mountain',
  'Chattanooga',
  'Gatlinburg',
  'Riceville ',
  'Greeneville',
  'Farragut',
];
const data = {
  labels,
  datasets: [
    {
      label: 'Cities',

      data: [
        5177, 331, 3731, 1381, 4783, 3625, 4793, 3407, 3807, 3501, 2617, 2653, 2917, 4817, 3141, 3985, 2295, 711, 607,
        2897, 2185, 3937, 3557, 2917, 629, 3451, 2841, 173, 2565, 1343, 2955, 899, 2021, 1509, 705, 451, 2299, 2341,
        1819, 869, 1809, 1045, 127, 583, 5, 1271, 2303, 2149, 52365,
      ],
      backgroundColor: [
        'rgba(99, 132, 255, 0.2)',
        'rgba(99, 0, 132, 0.2)',
        'rgba(255, 99, 132, 0.2)',
        'rgba(255, 159, 64, 0.2)',
        'rgba(255, 205, 86, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(54, 162, 235, 0.2)',
        'rgba(153, 102, 255, 0.2)',
        'rgba(201, 203, 207, 0.2)',
      ],
      borderColor: [
        'rgba(99, 132, 255)',
        'rgba(99, 0, 132)',
        'rgb(255, 99, 132)',
        'rgb(255, 159, 64)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        'rgb(54, 162, 235)',
        'rgb(153, 102, 255)',
        'rgb(201, 203, 207)',
      ],
      borderWidth: 1,
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
  },
};

const Donut = () => {
  return (
    <div className={homeStyle.main}>
      <h2>Bar Sample with Next.js</h2>
      <Doughnut
        data={data}
        options={{
          maintainAspectRatio: false,
        }}
      />
    </div>
  );
};
export default Donut;

export const StateRevenueDonut = () => {
  return (
    <div className={homeStyle.main}>
      <h2>Revenue by City</h2>
      <Pie data={data} options={options} />
    </div>
  );
};
